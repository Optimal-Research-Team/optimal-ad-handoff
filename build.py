"""Build the Optimal ad hand-off site (GitHub Pages) from the meta-ad-studio outputs.

    python3 build.py              # stage files + write index.html (local preview: python3 -m http.server)
    python3 build.py --publish    # ... then upload the full-quality files to the GitHub release and push the site

Small files (previews, posters, static PNGs, thumbnails, covers, captions) live in the repo and are served by Pages.
Full-quality videos and the zips are GitHub release assets (Pages and git both choke on 50 MB+ files).
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.join(HERE, "..", "meta-ad-studio")
REPO = "Optimal-Research-Team/optimal-ad-handoff"
TAG = "2026-10-12"
ROUND = "October 12–19, 2026"
REL = f"https://github.com/{REPO}/releases/download/{TAG}/"
STAGE = os.path.join(HERE, "release")          # git-ignored: what gets uploaded to the release

SERVICES = {
    "longevity": dict(name="Longevity membership", dest="https://www.beoptimal.ca/membership",
                      utm="utm_source={{site_source_name}}&utm_medium=paid&utm_campaign={{campaign.id}}&utm_term={{adset.id}}&utm_content={{ad.id}}"),
    "menopause": dict(name="Menopause", dest="https://www.beoptimal.ca/services/menopause-and-perimenopause-care",
                      utm="utm_source={{site_source_name}}&utm_medium=paid&utm_campaign={{campaign.id}}&utm_term={{adset.id}}&utm_content={{ad.id}}"),
    "cycle": dict(name="Cycle & Hormone Care", dest="https://www.beoptimal.ca/services/cycle-and-hormone-care",
                  utm="utm_source={{site_source_name}}&utm_medium=paid&utm_campaign={{campaign.id}}&utm_term={{adset.id}}&utm_content={{ad.id}}"),
}
# The shared tracker (Oct 28, Peter: "this has to integrate with a tracker for what content we have posted and where").
# A Google Sheet, one row per Meta ad name / post, edited by whoever uploads or posts (Jeremy, Peter, Claude's IG/FB sync).
# The page reads it live (gviz CSV: the sheet is link-viewable) and falls back to the copy fetched at build time.
TRACKER_ID = "10I29jiV4DCNSixJbTqPjM06sUSQxTZO7swV3yMabFxs"
TRACKER_EDIT = f"https://docs.google.com/spreadsheets/d/{TRACKER_ID}/edit"
TRACKER_KPI = f"https://docs.google.com/spreadsheets/d/{TRACKER_ID}/edit#gid=1126991466"   # Weekly KPIs tab (moved in Oct 28)
TRACKER_BASE = f"https://docs.google.com/spreadsheets/d/{TRACKER_ID}/gviz/tq?tqx=out:csv&headers=1&sheet="   # + Tracker | Sync%20log
# Meta's AI label ("AI info"): never turned on, for any ad or post (Peter, Oct 28), so the page doesn't track it.
# Oct 28 (Peter): cut the ads that weren't good enough, then close the gaps so codes run in order. The copy docs keep the
# original IDs; the page, the files and the tracker use the new ones.
CUT = {"M3": "price card only", "M5": "too abstract, no clear value", "MA1": "too abstract", "MB6": "looks too AI"}
RENAME = {"M4": "M3", "M6": "M4", "MA2": "MA1"}
CATALOG = []   # one entry per tracker row, filled while the page is built
# paid ads that also work as organic posts (real people or drawn graphics, nothing that would need an AI label)
ORGANIC_OK = {"MV1", "MV2", "MV3", "LV1", "LV2", "LV3", "CV1", "CV2", "CV3", "IRT1", "IRT2", "IRT3", "IRT4", "MA1"}


def cat(code, line, svc, fmt, anchor, thumb, base=None, kind="ad"):
    b = base or code
    CATALOG.append(dict(code=code, line=re.sub(r"[*{}]", "", line).replace("|", " "), svc=svc, fmt=fmt, anchor=anchor,
                        thumb=thumb, plan=plan_label(b), added=ADDED.get(b, ""), kind=kind, organic_ok=kind == "ad" and b in ORGANIC_OK))


def track(*codes):
    """placeholder the page fills from the tracker: where this ad is live"""
    return f'<div class="track" data-codes="{" ".join(codes)}"></div>'


VIDEOS = [  # id, service, folder in meta-ad-studio/out, render name, the line on screen
    ("LV1", "longevity", "longevity-core-v2", "LongevityCore", "3 things to know before you book."),
    ("LV2", "longevity", "longevity-ad2", "LongevityFullHour", "A full hour. Every year."),
    ("MV1", "menopause", "menopause-ad1", "MenopauseMyself", "“I just don’t feel like myself.”"),
    ("LV3", "longevity", "health-optimizer", "LongevityOptimize", "An hour with an NP who listens."),   # Oct 15, Rubeana
    # Oct 20, Chantelle Oostwoud, NP: a Tight cut (~MV1's length, so NP vs care coordinator is the one change) + a Flow cut
    ("MV2", "menopause", "meno-time-to-talk", "MenoTimeToTalk", "Menopause affects nearly every system.", [("T", "Tight"), ("F", "Flow")]),
    ("MV3", "menopause", "meno-three-things", "MenoThreeThings", "Patients tell me the same three things.", [("T", "Tight"), ("F", "Flow")]),
    # Oct 22, Cheryl: Cycle & Hormone Care, one cut each, labelled with the program badge from frame 0
    ("CV1", "cycle", "cycle-signs", "CycleSigns", "3 or more of these?", [("A", "Ad")]),
    ("CV2", "cycle", "cycle-told-normal", "CycleToldNormal", "“That’s just part of being a woman.”", [("A", "Ad")]),
    ("CV3", "cycle", "cycle-program-intro", "CycleProgramIntro", "Hormone care isn’t just for menopause.", [("A", "Ad")]),
]
CYCLE_R4 = ("CA1", "CA2", "CA3", "CA4", "CA5", "CP1", "CP2", "CD1", "CD2", "CE1", "CE2")   # Oct 28 round 4 singles (+ the CC carousel)
WAITING = {}   # was the Cycle & Hormone set; /services/cycle-and-hormone-care went live (Oct 28), so nothing is held
CYCLE_PLAN = {**{k: "Set 1 · general" for k in ("CV1", "CV2", "CV3", "CA1", "CA2", "CA3", "CA4", "CA5", "CC")},
              "CP1": "Set 2 · PMOS", "CP2": "Set 2 · PMOS", "CD1": "Set 2 · PMDD", "CD2": "Set 2 · PMDD",
              "CE1": "Set 2 · endometriosis", "CE2": "Set 2 · endometriosis",
              "CG1": "Google · general", "CG2": "Google · general", "CG3": "Google · PMOS", "CG4": "Google · PMDD",
              "CG5": "Google · endometriosis"}
SOCIALS = [  # organic-only reels: kept OFF the ads site (Peter, Oct 15), so the list stays empty; the format is kept for later
] and [
    ("RB1", "rubeana-bio", "RubeanaBio_Reel_9x16", "RubeanaBio_cover_9x16", "Meet Rubeana, our Clinical Director."),
    ("CI1", "cholesterol-info", "CholesterolInfo_Reel_9x16", "CholesterolInfo_cover_9x16", "Cholesterol, explained: HDL, LDL, Lp(a) and ApoB."),
]
CUTS = [("T", "Tight")]   # Oct 12 (Peter): Tight cuts only

# What to test first (Oct 12, 2026). One ad set per service, ~6 distinct ads each; the rest rotate in later.
#   ("now", rank, angle)   launch in wave 1, in priority order (tight budget: launch ranks 1-4 only)
#   ("next", None, angle)  a new angle to swap in when a wave-1 ad is cut
#   ("twin", "X", angle)   same message as X in a different look: swap in when X fatigues
PLAN = {
    # menopause (Oct 28: M3, M5, MA1, MB6 cut; old M4 → M3, M6 → M4, MA2 → MA1)
    "MV1": ("now", 1, "Emotional hook · video"),
    "MB1": ("now", 2, "Relatable moment · photo"),
    "MB5": ("now", 3, "Access, no referral · clinic photo"),
    "MB2": ("now", 4, "Symptom awareness · photo"),
    "MC":  ("now", 5, "How it works · carousel"),
    "MV3": ("next", None, "A/B vs MV1: the NP on camera, same offer · video"),
    "MV2": ("next", None, "NP explains the full-hour first visit · video"),
    "M2":  ("next", None, "60-minute first visit · big number"),
    "M1":  ("next", None, "Symptom list · education"),
    "MB4": ("next", None, "Hot flashes at work · photo"),
    "MB3": ("next", None, "NP-led, in Barrie · photo"),
    "MA1": ("next", None, "Midlife, planned for · botanical plate"),
    "M4":  ("twin", "MB1", "3 a.m. · night photo"),
    "M3":  ("twin", "MB5", "No referral · photo + capsule"),
    # longevity
    "LV1": ("now", 1, "A real person, trust · video"),
    "L1":  ("now", 2, "Price and value · ledger"),
    "L2":  ("now", 3, "Objection: my family doctor · diagram"),
    "LB1": ("now", 4, "Local awareness · photo"),
    "LB2": ("now", 5, "Speed · photo"),
    "LB3": ("now", 6, "Muscle, measured · photo"),
    "LV2": ("next", None, "A full hour, every year · video"),
    "LC":  ("next", None, "What $1,495 includes · carousel"),
    "L6":  ("next", None, "OHIP still covers labs · photo + capsule"),
    "LB4": ("next", None, "Written 12-month plan · photo"),
    "L3":  ("twin", "LB2", "Seen by Tuesday · calendar"),
    "L4":  ("twin", "LB3", "Every 90 days · figure + timeline"),
    "L5":  ("twin", "LV2", "An hour every year · illustration"),
    "LV3": ("twin", "LV2", "An hour with an NP who listens · NP video"),
    "LB5": ("twin", "L1", "NP for $1,495 a year · photo"),
    "LB6": ("twin", "L6", "OHIP covers labs · photo"),
    "LA1": ("twin", "LB5", "Two toonies a day · photo"),
    "LA2": ("next", None, "Normal is a range · gauge plate"),
}
# Hormozi pass (Oct 13, 2026): what changed on the image, and why.
REWRITES = [
    ("LB1", "Barrie has a new kind of health clinic.", "Your own Nurse Practitioner in Barrie, with same or next-day visits.", "Vague becomes a specific outcome. “New kind of clinic” says nothing; your own NP and next-day visits is the dream outcome."),
    ("LB2", "Same or next-day visits when something can’t wait.", "Sick today, seen tomorrow, by an NP who knows you.", "A scene the reader has lived, plus the relationship. Time delay goes to almost zero."),
    ("LB3", "Your body composition, measured every 90 days.", "Your muscle, measured every 90 days.", "Concrete beats abstract: it names the one thing worth measuring, and the copy explains why muscle matters more each decade."),
    ("LB4", "Every member gets a written 12-month plan.", "Know exactly what to do for your health this year.", "Sell the certainty, not the document."),
    ("LB5", "Your own Nurse Practitioner for $1,495 a year.", "Your own Nurse Practitioner for about $4 a day.", "The same price reframed per day ($1,495 ÷ 365)."),
    ("LB6", "Medically necessary labs are still covered by OHIP.", "OHIP still covers your medically necessary labs.", "Lead with the reassurance: the objection is answered in the first three words."),
    ("MB2", "Brain fog is a common perimenopause symptom.", "Brain fog can be perimenopause, not just a busy life.", "Names the wrong explanation she’s been giving herself, then reframes it. Curiosity, not a textbook line."),
    ("MB3", "Menopause care in Barrie, led by a Nurse Practitioner.", "Start menopause care in Barrie within days.", "Description becomes outcome plus speed. Cutting the time delay raises perceived value."),
    ("MB4", "Hot flashes don’t wait for a good time.", "Hot flashes don’t wait, and neither should you.", "Keeps the relatable hook and adds the push to act."),
    ("MB5", "No referral or family doctor needed.", "Menopause care without a referral or a family doctor.", "Says what it is in the first word. The old line never mentioned menopause, so a stranger couldn't tell what was on offer."),
    ("LA2", "Normal is a range. We talk about where you sit in it.", "Normal is a range, and we look at where you sit in it.", "Same idea, held to one sentence."),
    ("MC1", "It starts with a free 15-minute call.", "Menopause care in Barrie starts with a free 15-minute call.", "Card 1 has to say who and where, or nobody swipes."),
    ("MC4", "You get a written treatment plan.", "You get a written plan and the same NP every visit.", "Adds continuity: the same person at every visit, so the plan comes with someone who knows the history."),
    ("MC5", "Book your free call at beoptimal.ca.", "No referral needed: book your free call at beoptimal.ca.", "Removes the last objection right at the call to action."),
    ("LC1", "Here’s what $1,495 a year includes.", "Here’s everything $1,495 a year gets you.", "“Gets you” is about the reader, not the product."),
    ("LC5", "Book a free intro call at beoptimal.ca.", "Start with a free 15-minute call, no commitment.", "Risk reversal: free, short and no strings."),
]

# IV iron (Oct 14, 2026): pre-launch waitlist test on a Meta Instant Form. Oct 29 (Peter): the CTA is "Book now", to the IV iron page.
IRON = {  # id: (badge class, badge text)
    "IR1": ("now", "Run now"), "IRV1": ("now", "Run now"),   # IR3 removed Oct 20 (Peter: "delete IR3")
    "IR2": ("now", "Run now · cleared by the Clinical Director (Oct 20)"),
    # round 2 (Oct 19): one Hormozi lever each, all on the same founding-waitlist offer
    "IR4": ("now", "Test · time"), "IR5": ("now", "Test · effort"), "IR6": ("now", "Test · likelihood"),
    "IRM1": ("now", "Test · motion"), "IRM2": ("now", "Test · offer"), "IRV2": ("now", "Test · film"), "IRV3": ("now", "Test · film"),
    # Oct 20: Cheryl's four talking heads (real lounge, phone mic cleaned with DeepFilterNet)
    "IRT1": ("now", "Test · talking head"), "IRT2": ("now", "Test · talking head"), "IRT3": ("now", "Test · talking head"),
    "IRT4": ("now", "Test · talking head"),
}

SHOW_ID = {"MV1": "MV1-T", "LV1": "LV1-T", "LV2": "LV2-T", "LV3": "LV3-T", "MC": "MC1–5", "LC": "LC1–5"}
# Oct 19 (Peter): every ad ships in Meta's three ratios, full-bleed. 4:5 is retired (used only as a fallback if a file is missing).
RATIOS = [("9x16", "9:16 · Stories + Reels"), ("1x1", "1:1 · Feed"), ("1-91x1", "1.91:1 · Feed, right column, in-stream")]
SRATIOS = [("1x1", "1:1 Feed"), ("9x16", "9:16 Stories + Reels"), ("1-91x1", "1.91:1 Feed + right column")]


def simgs(folder, ad):
    """The static's files in Meta's three ratios (1:1 first: it's the thumbnail and the primary download)."""
    out = [(label, os.path.join(folder, f"{ad}_{r}.png")) for r, label in SRATIOS if os.path.exists(os.path.join(folder, f"{ad}_{r}.png"))]
    if not any(r == "1x1" for r, _ in SRATIOS if os.path.exists(os.path.join(folder, f"{ad}_{r}.png"))) and os.path.exists(os.path.join(folder, f"{ad}_4x5.png")):
        out.insert(0, ("4:5 Feed", os.path.join(folder, f"{ad}_4x5.png")))
    return out


def web_preview(src, rel):
    """A 720-wide H.264 preview + poster for the page, re-encoded only when the source is newer."""
    dst = os.path.join(HERE, rel)
    if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        ff = os.path.join(STUDIO, "tools/node_modules/ffmpeg-static/ffmpeg")
        subprocess.run([ff, "-y", "-v", "error", "-i", src, "-vf", "scale=720:-2:flags=lanczos,format=yuv420p", "-c:v", "libx264",
                        "-preset", "slow", "-crf", "27", "-maxrate", "2200k", "-bufsize", "4400k", "-c:a", "aac", "-b:a", "96k",
                        "-movflags", "+faststart", dst], check=True)
        subprocess.run([ff, "-y", "-v", "error", "-ss", "1.2", "-i", dst, "-frames:v", "1", "-q:v", "4", dst[:-4] + ".jpg"], check=True)
    return rel


def esc(s):
    return html.escape(s, quote=True)


def mb(path):
    return f"{os.path.getsize(path) / 1e6:.0f} MB" if os.path.getsize(path) > 1e6 else f"{os.path.getsize(path) / 1e3:.0f} KB"


def dur(path):
    fp = os.path.join(STUDIO, "tools/node_modules/ffprobe-static/bin/darwin/arm64/ffprobe")
    s = float(json.loads(subprocess.run([fp, "-v", "error", "-show_format", "-of", "json", path],
                                        capture_output=True, text=True).stdout)["format"]["duration"])
    s = round(s)
    return f"{s // 60}:{s % 60:02d}"


def put(src, rel):
    dst = os.path.join(HERE, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    return rel


def stage(src, name):
    """Copy into the release staging dir only when changed, so a rebuild never rewrites a file mid-upload."""
    os.makedirs(STAGE, exist_ok=True)
    dst = os.path.join(STAGE, name)
    if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src) or os.path.getmtime(src) > os.path.getmtime(dst):
        shutil.copy2(src, dst)
    return REL + name


def thumb(src, rel, width=480):
    dst = os.path.join(HERE, rel)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    im = Image.open(src).convert("RGB")
    im.resize((width, round(im.height * width / im.width)), Image.LANCZOS).save(dst, quality=84)
    return rel


# ------------------------------------------------------------------ copy, parsed from the source docs
def video_copy():
    doc = open(os.path.join(STUDIO, "VIDEO-ADS.md")).read()
    out = {}
    for m in re.finditer(r"### (\w+) · ([^\n]+)\n\n\*\*Primary text \(short\)\*\*\n(.*?)\n\n\*\*Primary text \(long\)\*\*\n(.*?)\n\n"
                         r"\*\*Headline:\*\* (.*?)(?: · \*\*Alt headline:\*\* (.*?))? · \*\*Description:\*\* (.*?)\n", doc, re.S):
        out[m[1]] = dict(short=m[3].strip(), long=m[4].strip(), headline=m[5], alt=m[6], description=m[7])
    for m in re.finditer(r"### (\w+) caption\n(.*?)(?=\n### |\n---|\Z)", doc, re.S):
        out.setdefault(m[1], {})["caption"] = m[2].strip()
    return out


def static_copy():
    r1 = open(os.path.join(STUDIO, "static/COPY.md")).read()
    r2 = open(os.path.join(STUDIO, "static/COPY-R2.md")).read()
    one = {m[1]: dict(title=m[2], primary=m[3].strip(), headline=m[4], description=m[5])
           for m in re.finditer(r"### ([ML]\d) · ([^\n]+)\n\*\*Primary text\*\*\n(.*?)\n\n\*\*Headline:\*\* (.*?) · \*\*Description:\*\* (.*?)\n", r1, re.S)}
    two = {m[1]: dict(title=m[2], primary=m[3], headline=m[4])
           for m in re.finditer(r"^\| ([ML]B\d) \| (.*?) \| (.*?) \| (.*?) \|$", r2, re.M)}
    car = {}
    for key, sec in (("MC", "Menopause carousel"), ("LC", "Longevity carousel")):
        body = r2.split(f"## {sec}")[1].split("\n## ")[0]
        car[key] = dict(primary=re.search(r"\*\*Primary text:\*\* (.*)", body)[1],
                        cards=re.findall(rf"^\| ({key}\d) \| (.*?) \| (.*?) \|$", body, re.M))
    r3 = open(os.path.join(STUDIO, "static/COPY-R3.md")).read()
    three = {m[1]: dict(title=m[2], primary=m[3].strip(), headline=m[4], description=m[5].strip())
             for m in re.finditer(r'### ((?:MA|LA)\d) · "(.*?)"\n\*\*Primary text:\*\* (.*?)\n\*\*Headline:\*\* (.*?) · \*\*Description:\*\* (.*?)\n', r3)}
    return one, two, car, three


def iron2_copy():
    doc = open(os.path.join(STUDIO, "static/COPY-IRON-R2.md")).read()
    return {m[1]: dict(title=m[2], short=m[3].strip(), long=m[4].strip(), headline=m[5], description=m[6].strip())
            for m in re.finditer(r'### (IR[MVT]?\d) · "(.*?)"[^\n]*\n\*\*Primary text \(short\):\*\* (.*?)\n\*\*Primary text \(long\):\*\* (.*?)\n'
                                 r'\*\*Headline:\*\* (.*?) · \*\*Description:\*\* (.*?)\n', doc)}


def iron_copy():
    doc = open(os.path.join(STUDIO, "static/COPY-IRON.md")).read()
    return {m[1]: dict(title=m[2], primary=m[3].strip(), headline=m[4], description=m[5].strip())
            for m in re.finditer(r'### (IRV?\d) · "(.*?)"[^\n]*\n\*\*Primary text:\*\* (.*?)\n\*\*Headline:\*\* (.*?) · \*\*Description:\*\* (.*?)\n', doc)}


def cycle_copy():
    """Cycle & Hormone Care statics, round 4 (Oct 28): Set 1 general CA1-CA5, Set 2 by condition CP/CD/CE (COPY-CYCLE.md)"""
    doc = open(os.path.join(STUDIO, "static/COPY-CYCLE.md")).read()
    return {m[1]: dict(title=m[2], primary=m[3].strip(), headline=m[4], description=m[5].strip())
            for m in re.finditer(r'### (C[APDE]\d) · "(.*?)"[^\n]*\n\*\*Primary text:\*\* (.*?)\n\*\*Headline:\*\* (.*?) · \*\*Description:\*\* (.*?)\n', doc)}


def cycle_carousel():
    """Cycle & Hormone Care carousel CC1-CC6 (Oct 28, round 4): shared primary text + one headline per card"""
    doc = open(os.path.join(STUDIO, "static/COPY-CYCLE.md")).read()
    return dict(primary=re.search(r"\*\*Carousel primary text:\*\* (.*)", doc)[1].strip(),
                cards=re.findall(r"^\| (CC\d) \| (.*?) \| (.*?) \|$", doc, re.M))


def google_groups(name="GOOGLE-ADS-CYCLE.md"):
    """Ad groups of a Google build sheet: [(id, title, keywords, headlines, descriptions)]"""
    doc = open(os.path.join(STUDIO, "static", name)).read()
    out = []
    for g in re.split(r"\n## ", doc):
        m = re.match(r"((?:CG|IRG)\d) · ([^\n]+)", g)
        if not m:
            continue
        kw = re.findall(r"^- `(.*?)`", g.split("**Headlines")[0], re.M)
        clean = lambda l: re.sub(r"\s*\*\(.*?\)\*", "", re.sub(r"^\d+\.\s*", "", l)).strip()
        hs = [clean(l) for l in re.search(r"\*\*Headlines \(15\):\*\*\n(.*?)\n\n", g, re.S)[1].splitlines()]
        ds = [clean(l) for l in re.search(r"\*\*Descriptions \(4\):\*\*\n(.*?)(?:\n\n|\Z)", g, re.S)[1].splitlines()]
        pin = re.search(r"^1\. (.*?) \*\(pin", g, re.M)
        path = re.search(r"\*\*Display path:\*\* `beoptimal\.ca/(.*?)`", g)
        out.append((m[1], m[2], kw, hs, ds, pin[1] if pin else None, path[1] if path else "cycle-care/barrie"))
    return out


def google_assets(name="GOOGLE-ADS-CYCLE.md"):
    """Campaign-level assets: sitelinks [(text, line 1, line 2)] (ones still waiting on a check left out), callouts, snippet"""
    doc = open(os.path.join(STUDIO, "static", name)).read()
    table = re.search(r"\*\*Sitelinks:\*\*\n\n\|.*?\n\|.*?\n(.*?)\n\n", doc, re.S)[1]
    links = [[c.strip() for c in row.strip("|").split("|")] for row in table.splitlines()]
    snip = re.search(r"\*\*Structured snippet\*\* \(header: (.*?)\): (.*)", doc)
    return dict(sitelinks=[l for l in links if "*(" not in l[0]],
                callouts=[c.strip() for c in re.search(r"\*\*Callouts:\*\* (.*)", doc)[1].split("·")],
                snippet=(snip[1], [v.strip() for v in snip[2].split("·")]))


def serp(hs, ds, path, assets, mobile=False):
    """How a responsive search ad can look on Google (desktop or phone), from the measured SERP styles (Oct 28, 2026)."""
    title = " | ".join([hs[0], hs[1], hs[2]] if not mobile else [hs[0], hs[3]])
    desc = (f"{ds[0]} {ds[1]}" if not mobile else ds[2])
    crumbs = " › ".join(path.split("/"))
    head = (f'<div class="g-spons">Sponsored</div><div class="g-head"><span class="g-fav"><img src="files/g-favicon.png" alt=""></span>'
            f'<span class="g-site"><span class="g-name">Optimal Health</span><span class="g-url">https://www.beoptimal.ca › {esc(crumbs)}</span></span>'
            f'<span class="g-dots" aria-hidden="true">⋮</span></div>')
    body = f'<div class="g-title">{esc(title)}</div><div class="g-desc">{esc(desc)}</div>'
    if not mobile:      # callouts and the snippet can show too, but Google rarely shows every extra at once
        body += '<div class="g-sl">' + "".join(f'<div><span class="g-slt">{esc(t)}</span><span>{esc(a)}</span><span>{esc(b)}</span></div>'
                                               for t, a, b in assets["sitelinks"][:4]) + "</div>"
    else:
        body += '<div class="g-slm">' + "".join(f'<div><span>{esc(t)}</span><i>›</i></div>' for t, *_ in assets["sitelinks"][:3]) + "</div>"
    return f'<div class="serp{" m" if mobile else ""}">{head}{body}</div>'


# ------------------------------------------------------------------ html pieces
def copy_field(label, text, rows=None):
    t = esc(text)
    body = f'<textarea readonly rows="{rows}">{t}</textarea>' if rows else f'<div class="val">{t}</div>'
    return (f'<div class="field"><div class="flabel">{esc(label)}<button class="copy" data-copy="{t}">Copy</button></div>'
            f'{body}</div>')


def ad_names(vid, cuts):
    if len(cuts) == 1:
        return f"Ad name <code>{vid}-{cuts[0][0]}</code>. Upload its three files as one ad."
    extra = " MV3-T is also the Chantelle vs Cheryl test against MV1-T." if vid == "MV3" else ""
    return (f"Two ads, <code>{vid}-T</code> (short) and <code>{vid}-F</code> (longer), in the same ad set as a Meta A/B test "
            f"on length. Upload each cut's three files as one ad.{extra}")


def badge(ad):
    if ad in IRON:
        return f'<span class="plan {IRON[ad][0]}">{esc(IRON[ad][1])}</span>'
    st, x, _ = PLAN.get(ad, (None, None, None))
    if st == "now":
        return f'<span class="plan now">Test now · #{x}</span>'
    if st == "next":
        return '<span class="plan next">Next up</span>'
    if st == "twin":
        return f'<span class="plan twin">Twin of {SHOW_ID.get(x, x)}</span>'
    return ""


def plan_html(thumbs, titles):
    """The 'what to test first' block: per service, wave 1 in priority order, then next-up and twins."""
    cols = []
    for svc, pre in (("menopause", "M"), ("longevity", "L")):
        ids = [k for k in PLAN if k.startswith(pre)]
        now = sorted([k for k in ids if PLAN[k][0] == "now"], key=lambda k: PLAN[k][1])
        nxt = [k for k in ids if PLAN[k][0] == "next"]
        twn = [k for k in ids if PLAN[k][0] == "twin"]
        rows = "".join(
            f'<a class="prow" href="#{k}"><span class="rank">{PLAN[k][1]}</span>'
            f'<img src="{thumbs.get(k, "")}" alt="" loading="lazy"><span class="pt"><b>{SHOW_ID.get(k, k)}</b>'
            f'<span>{esc(titles.get(k, ""))}</span><small>{esc(PLAN[k][2])}</small></span></a>' for k in now)
        nexts = "".join(f'<a class="pchip" href="#{k}"><b>{SHOW_ID.get(k, k)}</b> {esc(PLAN[k][2])}</a>' for k in nxt)
        twins = "".join(f'<a class="pchip twin" href="#{k}"><b>{SHOW_ID.get(k, k)}</b> twin of {SHOW_ID.get(PLAN[k][1], PLAN[k][1])}</a>'
                        for k in twn)
        cols.append(f'''
      <div class="card pcol"><span class="svc {svc}">{SERVICES[svc]["name"]}</span>
        <h4>Test now <em>· launch in this order</em></h4><div class="prows">{rows}</div>
        <h4>Next up <em>· new angles for when you cut one</em></h4><div class="pchips">{nexts}</div>
        <h4>Twins <em>· same message, new look, for when one fatigues</em></h4><div class="pchips">{twins}</div>
      </div>''')
    return "".join(cols)


def rewrites_html(thumbs):
    rows = []
    for k, before, after, why in REWRITES:
        anchor = k[:2] if k[:2] in ("MC", "LC") else k
        rows.append(f'''<div class="rw"><a href="#{anchor}"><img src="{thumbs.get(k, "")}" alt="{k}" loading="lazy"></a>
          <div class="rwt"><span class="id">{SHOW_ID.get(k, k)}</span> {badge(k)}
            <p class="before">{esc(before)}</p><p class="after">{esc(after)}</p><p class="why">{esc(why)}</p></div></div>''')
    return "".join(rows)


def dl(href, label, size, primary=False):
    return (f'<a class="dl{" primary" if primary else ""}" href="{esc(href)}" download>'
            f'<span>{esc(label)}</span><em>{esc(size)}</em></a>')


# ------------------------------------------------------------------ Oct 20 2026 rebuild: by service, dated, IR3 gone
UPDATED = "Oct 29, 2026"
LATEST = "2026-10-29"
D12, D13, D14, D15, D19, D20, D21, D22, D26, D28, D29 = ("2026-10-12", "2026-10-13", "2026-10-14", "2026-10-15", "2026-10-19",
                                                         "2026-10-20", "2026-10-21", "2026-10-22", "2026-10-26", "2026-10-28",
                                                         "2026-10-29")
ADDED = {**{k: D12 for k in ("M1 M2 M3 M4 M5 M6 L1 L2 L3 L4 L5 L6 MB1 MB2 MB3 MB4 MB5 MB6 LB1 LB2 LB3 LB4 LB5 LB6 "
                             "MC LC LV1 LV2 MV1").split()},
         **{k: D13 for k in ("MA1", "MA2", "LA1", "LA2")},
         **{k: D14 for k in ("IR1", "IR2", "IRV1")},
         "LV3": D15,
         **{k: D19 for k in ("IR4", "IR5", "IR6", "IRM1", "IRM2", "IRV2", "IRV3")},
         **{k: D20 for k in ("IRT1", "IRT2", "IRT3", "IRT4", "MV2", "MV3")},
         **{k: D22 for k in ("CV1", "CV2", "CV3", "CC", "CG1", "CG2", "CG3", "CG4")},
         **{k: D28 for k in CYCLE_R4}}
ADDED = {RENAME.get(k, k): v for k, v in ADDED.items() if k not in CUT}
CHANGED = {"IR1": (D20, "new image and headline"), "IR2": (D20, "new image: the website hero"),
           "IRV1": (D20, "rebuilt from the website hero, animated"),
           "MV2": (D21, "blood-draw and body-scan pictures; softer opening"),
           "MV3": (D21, "hormone-levels chart from the menopause page; softer opening"),
           "CB2": (D21, "pause at 0:42 cut; softer opening"),
           "CB1": (D21, "opening shot and the 0:30 graphic cut"),
           **{k: (D21, "softer opening (room tone, not silence)") for k in ("MI1", "MI2", "MI3")}}
CHANGED["MI2"] = (D26, "new cover: Chantelle smiling, not mid-word")
CHANGED["CC"] = (D28, "redone as 6 cards; card 1 now names the symptoms")
CHANGED["CA5"] = (D28, "says \u201cmenstrual cycle\u201d")
CHANGED["CE2"] = (D28, "\u201cpain with intimacy\u201d")
CHANGED.update({new: (D28, f"renamed from {old}") for old, new in RENAME.items()})
CHANGED.update({g: (D28, "rewritten as five ad groups") for g in ("CG1", "CG2", "CG3", "CG4")})
ADDED.update({g: D28 for g in ("IRG1", "IRG2", "IRG3", "IRG4")})
ADDED["CG5"] = D28
# Oct 29 (Peter): IV iron's call to action is "Book now", not the founding waitlist
CHANGED.update({k: (D29, "Book now end card; the waitlist line is cut") for k in ("IRT1", "IRT2", "IRT3", "IRT4", "IRV2", "IRV3")})
CHANGED.update({k: (D29, "Book now end card") for k in ("IRV1", "IRM1")})
CHANGED["IRM2"] = (D29, "reworked: what you get, then Book now")
CHANGED.update({k: (D29, "copy says Book now") for k in ("IR1", "IR2", "IR4", "IR5", "IR6")})
CHANGED.update({k: (D29, "Book now, no waitlist") for k in ("IRG1", "IRG2", "IRG3", "IRG4")})
REMOVED = {"IR3": D20}
SHORT = {"9x16": "9:16", "1x1": "1:1", "1-91x1": "1.91:1"}
NEWS = [  # (date, what happened, ids that link to cards, ids removed)
    (D29, "IV iron now says Book now, not \u201cjoin the founding waitlist\u201d. Every IV iron video has a new end card (\u201cBook your IV iron visit.\u201d with a Book now button), and the spoken \u201cjoin the waitlist\u201d lines are cut from the talking heads and the voiceover films. IRM2 used to sell the free waitlist, so it now lists what you get, start to finish. All the IV iron copy and the Google search ads end on booking. The Meta button is Book now and the destination is the IV iron page, which still shows the waitlist form: its buttons need to open booking before these go live.",
     ["IRV1", "IRT1", "IRT2", "IRT3", "IRT4", "IRV2", "IRV3", "IRM1", "IRM2", "IR1", "IR2", "IR4", "IR5", "IR6", "IRG1", "IRG2", "IRG3", "IRG4"], []),
    (D28, "Cut four ads that weren't good enough: M3 (just a price card), M5 and MA1 (too abstract) and MB6 (looks too AI). "
          "The rest were renamed so the codes run in order: M4 is now M3, M6 is now M4, MA2 is now MA1. The old M3 is still "
          "running in Ads Manager, so switch it off. The Cycle & Hormone Care page is live, so nothing is on hold any more. "
          "CA5 now says \u201cmenstrual cycle\u201d, the carousel's first card names the symptoms, and CE2 and CC5 say "
          "\u201cpain with intimacy\u201d. Google search for Cycle & Hormone Care is now five ad groups, two general (CG1, CG2) and "
          "three by condition (CG3 PMOS, CG4 PMDD, CG5 endometriosis), each shown the way it looks on Google. "
          "IV iron's Google search ads were rewritten the same way (IRG1–IRG4). Meta's AI label stays off for every ad and post.",
     ["M3", "M4", "MA1", "CA5", "CC", "CE2", "CG1", "CG2", "CG3", "CG4", "CG5", "IRG1", "IRG2", "IRG3", "IRG4"], ["M3 (cut)", "M5", "MA1 (cut)", "MB6"]),
    (D28, "Cycle & Hormone Care statics redone in two sets. Set 1 (general) covers every symptom the program looks at: five "
          "single-image ads (CA1–CA5) and a 6-card carousel (CC1–CC6) with one symptom group per card. Set 2 (by condition) "
          "has two ads each for PMOS (formerly PCOS), PMDD and endometriosis (CP, CD, CE). They describe the signs and never "
          "ask \u201cDo you have…?\u201d, which Meta rejects. The earlier statics (CS1–CS7 and the 5-card carousel) are retired. Also new: the Overview, which shows "
          "where every ad and post is live (Meta, Instagram, Facebook, Google) from the shared tracker sheet, checked every day.", ["CA1", "CA2", "CA3", "CA4", "CA5", "CC", "CP1", "CP2", "CD1", "CD2", "CE1", "CE2"], ["CS3–CS6"]),
    (D26, "Instagram check: nothing new has gone up since Oct 24 apart from the member portal teaser (Oct 26). MI2 (brain fog) was taken down for its cover, which caught "
          "Chantelle mid-word, and reposted on Oct 26 with a new cover (a smiling frame). MA2 is live as an organic feed post (since Oct 23), and its card "
          "now says so. Two drawn 3-D equipment reels went up on Oct 24 (the InBody 580 and the KICKR BIKE); they aren't ads, so "
          "they have no cards here. New rule for organic posts (Peter, Oct 24): nothing that needs Meta's AI label goes on "
          "Instagram or Facebook.", ["ig-MI2", "MA2"], []),
    (D22, "New service: Cycle & Hormone Care. Cheryl's three video ads (labelled with the program from the first frame), four "
          "single statics that each stand alone, one 5-card carousel that tells the story in order (hook, symptoms can "
          "connect, how we look, 12 weeks, free Cycle Check), and a Google search campaign in four ad groups. Hold everything "
          "until the Cycle & Hormone Care page is live (the URL 404s today). (Replaced on Oct 28: the statics are now Set 1 and Set 2, "
          "Google has five ad groups, and the page is live.)",
     ["CV1", "CV2", "CV3", "CC", "CG1", "CG2", "CG3", "CG4"], ["CS3–CS6"]),
    (D21, "Eight Instagram posts went live, alternating menopause and IV iron: CB1, CB2, MI1, IRT2, MI2, IRT3, MI3, IRT4 "
          "(IRT1 was already up). None are on Facebook yet. Chantelle's videos: her name title now opens over the room's "
          "sound instead of dead silence. MV2 shows a blood draw, then the body composition scan. MV3 uses the "
          "hormone-levels chart from the menopause page. CB1 loses its opening shot and the 0:30 graphic, and CB2 loses the "
          "pause at 0:42.", ["ig-CB1", "ig-CB2", "ig-MI1", "ig-IRT2", "ig-MI2", "ig-IRT3", "ig-MI3", "ig-IRT4", "MV2", "MV3"], []),
    (D20, "Chantelle's menopause video ads, each in a Tight and a Flow cut. Cheryl's four IV iron talking heads. IR1 and IR2 "
          "redone with clearer images (IR2 uses the website hero), and IRV1 rebuilt from the hero. IR3 removed. Nine Instagram "
          "posts added, most not posted yet.",
     ["MV3", "MV2", "IRT1", "IRT2", "IRT3", "IRT4", "IR1", "IR2", "IRV1", "ig-MI1", "ig-MI2", "ig-MI3", "ig-CB1", "ig-CB2",
      "ig-IRT1", "ig-IRT2", "ig-IRT3", "ig-IRT4"], ["IR3"]),
    (D19, "IV iron round 2, one Hormozi lever per ad. Every earlier ad re-made in Meta's three ratios (1:1, 9:16, 1.91:1), "
          "so nothing gets cropped or boxed. AI-invented clinic rooms retired.", ["IR4", "IR5", "IR6", "IRM1", "IRM2", "IRV2", "IRV3"], []),
    (D15, "Rubeana's longevity video ad, plus two organic posts.", ["LV3", "ig-RB1", "ig-CI1"], []),
    (D14, "IV iron pre-launch: the founding-waitlist ads on a Meta Instant Form.", ["IR1", "IR2", "IRV1"], []),
    (D13, "Round 3 engraved concepts, and the Hormozi rewrite of every image line (see How to launch).", ["MA1", "MA2", "LA1", "LA2"], []),
    (D12, "The first set: Cheryl's three videos, round 1 and round 2 statics for both services, and both carousels.",
     ["MV1", "LV1", "LV2", "M3", "MB1", "MB5", "MC", "L1", "L2", "LB1", "LC"], []),
]
NEWS = [(d, re.sub(r"\b(" + "|".join(RENAME) + r")\b", lambda m: f"{m[1]} (now {RENAME[m[1]]})", t) if d < D28 else t,
         [i if d >= D28 else "ig-" + RENAME.get(i[3:], i[3:]) if i.startswith("ig-") else RENAME.get(i, i) for i in ids if i not in CUT or d >= D28],
         gone) for d, t, ids, gone in NEWS]
# organic Instagram posts (not ads): id, folder in meta-ad-studio/out, render name, line, added, status
# static ads that also went up on Instagram as organic feed posts: id -> (post shortcode, date)
IG_STATIC = {"MA1": ("De2kqQAFkhP", "Oct 23")}   # MA1 was MA2 until Oct 28
IG_LINK = {"IRT1": "DeuqtE3ux0g", "CB1": "DexGHdyuXk0", "CB2": "DexGpqDuUb-", "MI1": "DexHDf2ulLf", "IRT2": "DexHYHRuWz5",
           "MI2": "De-Ln2wOrGr", "IRT3": "DexIED5u8No", "MI3": "DexId1Pusbd", "IRT4": "DexI9NouTrG"}   # posted Oct 20-21
POSTS = [
    ("MI1", "meno-not-stupider", "MenoNotStupider", "You're not getting stupider.", D20, "posted Oct 21"),
    ("MI2", "meno-brain-fog", "MenoBrainFog", "Your brain fog has an explanation.", D20, "posted Oct 26"),
    ("MI3", "meno-in-your-head", "MenoInYourHead", "It is all in your head, just not the way you think.", D20, "posted Oct 21"),
    ("CB1", "chantelle-bio", "ChantelleBio", "Meet Chantelle, PHC-NP.", D20, "posted Oct 21"),
    ("CB2", "chantelle-four-things", "ChantelleFourThings", "4 things I tell every new patient.", D20, "posted Oct 21"),
    ("IRT1", "iron-pills-dont-work", "IronPills", "Iron pills don't work for everyone.", D20, "posted Oct 20"),
    ("IRT2", "iron-not-anemia", "IronNotAnemia", "Low iron doesn't always look like anemia.", D20, "posted Oct 21"),
    ("IRT3", "iron-three-things", "IronThreeThings", "Three things most people don't know about IV iron.", D20, "posted Oct 21"),
    ("IRT4", "iron-what-it-looks-like", "IronWhatItLooksLike", "Here's what getting IV iron actually looks like.", D20, "posted Oct 21"),
    ("RB1", "rubeana-bio", "RubeanaBio", "Meet Rubeana, our Clinical Director.", D15, "posted Oct 15"),
    ("CI1", "cholesterol-info", "CholesterolInfo", "Cholesterol, explained: HDL, LDL, Lp(a) and ApoB.", D15, "posted Oct 15"),
]


def fmt(d):
    m = {"10": "Oct", "11": "Nov", "09": "Sep"}[d[5:7]]
    return f"{m} {int(d[8:])}"


def when(ad, added=None):
    """(changed today, '', a short stamp). Only today's changes get a stamp; the change log keeps the history."""
    a = added or ADDED.get(ad)
    u = CHANGED.get(ad)
    if a == LATEST:
        return True, "", f'<span class="stamp new">New today</span>'
    if u and u[0] == LATEST:
        return True, "", f'<span class="stamp new">Updated today · {esc(u[1])}</span>'
    return False, "", ""


def khead(code, *meta):
    """the line above a card's title: its code, then what it is and where it sits in the plan"""
    bits = " · ".join(esc(m) for m in meta if m)
    return f'<div class="khead"><span class="kcode">{esc(code)}</span>{f"<span class=kmeta>{bits}</span>" if bits else ""}</div>'




def plan_label(ad):
    """the plan column, as plain text"""
    if ad in WAITING:
        return "Hold: page not live"
    if ad in IRON:
        return IRON[ad][1].split(" · cleared")[0]
    if ad in CYCLE_PLAN:
        return CYCLE_PLAN[ad]
    if ad.startswith("IRG"):
        return "Google · IV iron"
    st, x, _ = PLAN.get(ad, (None, None, None))
    return {"now": f"Test now #{x}", "next": "Next up", "twin": f"Twin of {SHOW_ID.get(x, x)}"}.get(st, "")


def order(ad):
    st, x, _ = PLAN.get(ad, (None, None, None))
    return ({"now": 0, "next": 1, "twin": 2}.get(st, 3), x if st == "now" else 0, ad)


def kv(k, v, copy=False):
    btn = f'<button class="copy" data-copy="{esc(v)}">Copy</button>' if copy else ""
    return f'<div class="kv"><div class="k">{esc(k)}{btn}</div><div class="v">{esc(v)}</div></div>'


CHECKLIST = '''
  <label class="check"><input type="checkbox" data-k="g-sets"><span><b>Few ads, videos first:</b> 4–6 ads per ad set, mostly videos plus a couple of statics. At our budgets Meta can only give that many a fair test. One ad set per service, images and videos together (Cycle has two: general and by condition). <small>Oct 29 plan (Peter): don't upload every ad; the rest is a queue.</small></span></label>
  <label class="check"><input type="checkbox" data-k="g-m"><span><b>Menopause:</b> keep MV1-T, MV2-T, MV3-T, MB1 and MB5 running, and switch off the old M3 (the price card, cut Oct 28). No new ads this round. Set MB1's description to \u201cFree 15-min call \u00b7 No referral\u201d.</span></label>
  <label class="check"><input type="checkbox" data-k="g-l"><span><b>Longevity:</b> rebuild LV1-T with the real LV1 video (it has been running MV1's) and add LV2-T. Put the two videos in their own ad set with a small daily minimum for 7 days, so they get a fair read next to L1, L2 and LB1.</span></label>
  <label class="check"><input type="checkbox" data-k="g-cv"><span><b>Cycle &amp; Hormone Care:</b> the landing page is live. Meta, two ad sets for women 18–45, budget split evenly: <b>Set 1 · general</b> CV1-A, CV2-A, CV3-A and the CC carousel; <b>Set 2 · by condition</b> CP1, CP2 (PMOS), CD1, CD2 (PMDD), CE1, CE2 (endometriosis). <small>Oct 29 (Peter): push the condition statics too.</small> Google: build from <a href="files/GOOGLE-ADS-CYCLE.md" target="_blank" rel="noopener">GOOGLE-ADS-CYCLE.md</a> (five ad groups).</span></label>
  <label class="check"><input type="checkbox" data-k="g-ir"><span><b>IV iron (opens next week):</b> once the IV iron page's buttons open booking, Meta: IRV1, IRT1, IRT2 and IR1 with the <b>Book now</b> button, and Google from <a href="files/GOOGLE-ADS-IRON.md" target="_blank" rel="noopener">GOOGLE-ADS-IRON.md</a> (four ad groups, booking conversion first). Download the videos fresh: they were re-rendered Oct 29 with the Book now end card.</span></label>
  <label class="check"><input type="checkbox" data-k="g-ai"><span><b>Leave Meta's AI label off</b> for every ad and post (Peter, Oct 28).</span></label>
  <label class="check"><input type="checkbox" data-k="g-rot"><span><b>Every week:</b> turn off an ad that has spent about 1.5\u00d7 the cost per booking with no booking, and add the next one or two from the queue.</span></label>
  <label class="check"><input type="checkbox" data-k="g-track"><span><b>Mark it in the tracker</b> when an ad goes into Ads Manager, goes live or is paused: one row per ad name in the tracker sheet (top of the Overview). The daily check fills in what it can see.</span></label>
  <label class="check"><input type="checkbox" data-k="g-copy"><span><b>Name every ad with its ID</b> and paste the copy from its card. Keep the URL parameters exactly as written.</span></label>
  <label class="check"><input type="checkbox" data-k="g-pub"><span><b>Publish, then don't touch it for 7 days.</b></span></label>'''


def build():
    for d in ("previews-web", "files", "static-ads"):   # rebuilt every run
        shutil.rmtree(os.path.join(HERE, d), ignore_errors=True)
    vc = video_copy()
    r1, r2, car, r3 = static_copy()
    zips = {"videos": [], "r1": [], "r2": [], "r3": [], "r4": [], "r5": [], "r9": []}
    ir = iron_copy()
    ir2 = iron2_copy()
    social = open(os.path.join(STUDIO, "SOCIAL-VIDEOS.md")).read()
    iron2_doc = open(os.path.join(STUDIO, "static/COPY-IRON-R2.md")).read()
    n = dict(menopause=0, longevity=0, cycle=0, iron=0, ig=0)

    def thumbs_more(more):
        return f'<details class="more"><summary>Thumbnails + captions</summary><div class="dls">{"".join(more)}</div></details>' if more else ""

    def video_files(base_dir, stem_for, asset_for, zip_key, thumb_rel_for):
        """the three ratio files (+ thumbnails) for one cut"""
        files, more, d = [], [], None
        for r, _ in RATIOS:
            src = os.path.join(base_dir, stem_for(r) + ".mp4")
            if not os.path.exists(src):
                continue
            d = d or dur(src)
            files.append(dl(stage(src, asset_for(r)), SHORT[r], mb(src), primary=(r == "9x16")))
            th = os.path.join(base_dir, stem_for(r) + "_thumb.jpg")
            if os.path.exists(th):
                more.append(dl(put(th, thumb_rel_for(r)), f"Thumbnail {SHORT[r]}", mb(th)))
                zips[zip_key].append((th, os.path.basename(thumb_rel_for(r))))
        return files, more, d

    # ---------------- video ads (menopause + longevity)
    vids = {"menopause": [], "longevity": [], "cycle": []}
    for vid, svc, folder, name, line, *rest in sorted(VIDEOS, key=lambda v: order(v[0])):
        out = os.path.join(STUDIO, "out", folder)
        c = vc[vid]
        cuts = rest[0] if rest else CUTS
        cuts_html = []
        for k, cut in cuts:
            files, more, d = video_files(out, lambda r: f"{name}_{cut}_{r}", lambda r: f"{vid}-{k}_{cut}_{r}.mp4", "videos",
                                         lambda r: f"files/{vid}-{k}_thumbnail_{r}.jpg")
            srt = os.path.join(out, f"{name}_{cut}.srt")
            more.append(dl(put(srt, f"files/{vid}-{k}_captions.srt"), "Captions .srt (optional)", mb(srt)))
            prev = web_preview(os.path.join(out, f"{name}_{cut}_9x16.mp4"), f"previews/{name}_{cut}_9x16.mp4")
            cat(f"{vid}-{k}", line + ("" if len(cuts) == 1 else f" ({cut} cut)"), svc, "Video ad", vid, prev[:-4] + ".jpg", base=vid)
            cuts_html.append(f'''<div class="cut"><video src="{prev}" poster="{prev[:-4]}.jpg" controls playsinline preload="none"></video>
          <div class="cutname">{vid}-{k} · {cut} · {d}</div><div class="dls">{"".join(files)}</div>{thumbs_more(more)}</div>''')
        isnew, newpill, whenline = when(vid)
        alt = copy_field("Alt headline", c["alt"]) if c.get("alt") else ""
        n[svc] += 1
        vids[svc].append(f'''
    <article class="card ad{" isnew" if isnew else ""}" id="{vid}">
      <div class="cuts">{"".join(cuts_html)}</div>
      <div class="adtext">{khead(vid, "Video ad", plan_label(vid))}<h3>{esc(line)}</h3>{whenline}
        {track(*(f"{vid}-{k}" for k, _ in cuts))}
        <p class="note">{ad_names(vid, cuts)}</p>
        <details class="copybox"><summary>Copy to paste</summary>
          <div class="twocol">{copy_field("Headline", c["headline"])}{copy_field("Description", c["description"])}</div>{alt}
          {copy_field("Primary text (short)", c["short"], 3)}{copy_field("Primary text (long)", c["long"], 7)}</details>
      </div>
    </article>''')

    # ---------------- static ads
    def static_tile(ad, title, primary, headline, description, imgs, round_key, extra="", svc=None, fmt="", src_id=None):
        files = []
        for label, src in imgs:
            base = os.path.basename(src).replace(src_id, ad, 1) if src_id else os.path.basename(src)   # renamed ads ship under the new code
            rel = put(src, f"static-ads/{round_key}/{base}")
            files.append(dl(rel, label.split(" ")[0], mb(src), primary=label.startswith(("1:1", "4:5"))))
            zips[round_key].append((src, base))
        th = thumb(imgs[0][1], f"static-ads/{round_key}/thumbs/{ad}.jpg")
        isnew, newpill, whenline = when(ad)
        description = description or {"M": "Free 15-min call · No referral", "L": "About $4 a day · HSA eligible"}.get(ad[0]) if round_key == "r2" else description
        desc = copy_field("Description", description) if description else ""
        if svc:
            n[svc] += 1
            cat(ad, title, svc, "Image ad", ad, th)
        return f'''
      <article class="card tile{" isnew" if isnew else ""}" id="{ad}">
        <img src="{th}" alt="{esc(ad)}" loading="lazy">
        <div class="tbody">{khead(ad, fmt or "Image ad", plan_label(ad))}<h4>{esc(title)}</h4>{whenline}
          {track(ad)}
          <div class="dls">{"".join(files)}</div>
          <details class="more"><summary>Copy to paste</summary>{copy_field("Headline", headline)}{desc}{copy_field("Primary text", primary, 4)}{extra}</details>
        </div>
      </article>'''

    sdir = os.path.join(STUDIO, "static/out")
    statics = {"menopause": [], "longevity": []}
    rows = []   # (new id, title, primary, headline, description, images, round, original id); cut ads are left out
    for ad, c in r1.items():
        rows.append((RENAME.get(ad, ad), c["title"], c["primary"], c["headline"], c["description"],
                     simgs(os.path.join(sdir, "meno" if ad[0] == "M" else "long"), ad), "r1", ad))
    for ad, c in r2.items():
        rows.append((RENAME.get(ad, ad), c["title"], c["primary"], c["headline"], None,
                     simgs(os.path.join(sdir, "r2", "meno" if ad[0] == "M" else "long"), ad), "r2", ad))
    for ad, c in r3.items():
        rows.append((RENAME.get(ad, ad), c["title"], c["primary"], c["headline"], c["description"],
                     simgs(os.path.join(sdir, "r3", "meno" if ad[0] == "M" else "long"), ad), "r3", ad))
    rows = [r for r in rows if r[7] not in CUT]
    for *row, src in sorted(rows, key=lambda r: order(r[0])):
        svc = "menopause" if row[0][0] == "M" else "longevity"
        statics[svc].append(static_tile(*row, svc=svc, src_id=src if src != row[0] else None))

    carousels = {}
    for key, svc in (("MC", "menopause"), ("LC", "longevity")):
        sub = "meno-carousel" if key == "MC" else "long-carousel"
        cards = []
        for i, (cid, onimg, chead) in enumerate(car[key]["cards"], 1):
            src = os.path.join(sdir, "r2", sub, f"{cid}_card{i}_1x1.png")
            if not os.path.exists(src):
                src = os.path.join(sdir, "r2", sub, f"{cid}_card{i}.png")
            rel = put(src, f"static-ads/r2/{os.path.basename(src)}")
            zips["r2"].append((src, f"{key} carousel/{os.path.basename(src)}"))
            th = thumb(src, f"static-ads/r2/thumbs/{cid}.jpg", 360)
            cards.append(f'<figure><img src="{th}" alt="{cid}" loading="lazy"><figcaption><b>{cid}</b> · {esc(chead)}'
                         f'<div class="dls">{dl(rel, "Card", mb(src), True)}</div></figcaption></figure>')
        isnew, newpill, whenline = when(key)
        n[svc] += 1
        cat(key, f"Carousel, {len(cards)} cards: " + car[key]["cards"][0][1], svc, "Carousel ad", key,
            f"static-ads/r2/thumbs/{car[key]['cards'][0][0]}.jpg")
        carousels[svc] = f'''
    <div class="group"><h3>Carousel</h3><span>One ad with five 1:1 cards, in this order.</span></div>
    <article class="card carousel" id="{key}">{khead(f"{key}1–{key}5", "Carousel ad · 5 cards", plan_label(key))}<h3>{SERVICES[svc]["name"]} carousel</h3>{whenline}{track(key)}
      <div class="cards">{"".join(cards)}</div><details class="copybox"><summary>Copy to paste</summary>{copy_field("Primary text (shared by all 5 cards)", car[key]["primary"], 2)}</details></article>'''

    # ---------------- IV iron: videos (talking heads, the hero film, motion, films) + statics. IR3 removed Oct 20 (Peter).
    idir, i2dir = os.path.join(sdir, "r4", "iron"), os.path.join(sdir, "r5", "iron")
    KIND = {"IRT1": "Talking head: Cheryl in our lounge", "IRT2": "Talking head: Cheryl",
            "IRT3": "Talking head: Cheryl, three points", "IRT4": "Talking head: Cheryl, five steps",
            "IRV1": "The IV iron page's hero image, animated, silent",
            "IRV2": "Short film with a voiceover: our lounge and reception",
            "IRV3": "Short film with a voiceover: home still lifes and our lounge",
            "IRM1": "Motion graphics, silent", "IRM2": "Motion graphics, silent: what you get"}
    iron_videos = []
    for ad in ("IRV1", "IRT1", "IRT2", "IRT3", "IRT4", "IRV2", "IRV3", "IRM1", "IRM2"):   # Run now first, then the tests
        base, zk = (idir, "r4") if ad == "IRV1" else (i2dir, "r5")
        files, more, d = video_files(base, lambda r: f"{ad}_{r}", lambda r: f"{ad}_{r}.mp4", zk, lambda r: f"static-ads/{zk}/{ad}_thumbnail_{r}.jpg")
        if not files:
            continue
        prev = web_preview(os.path.join(base, f"{ad}_9x16.mp4"), f"previews/iron/{ad}_9x16.mp4")
        if ad == "IRV1":
            c = ir["IRV1"]
            text = f'{copy_field("Primary text", c["primary"], 5)}'
        else:
            c = ir2[ad]
            text = f'{copy_field("Primary text (short)", c["short"], 3)}{copy_field("Primary text (long)", c["long"], 6)}'
        isnew, newpill, whenline = when(ad)
        n["iron"] += 1
        cat(ad, c["title"], "iron", "Video ad", ad, prev[:-4] + ".jpg")
        iron_videos.append(f'''
    <article class="card ad{" isnew" if isnew else ""}" id="{ad}">
      <div class="cuts"><div class="cut"><video src="{prev}" poster="{prev[:-4]}.jpg" controls playsinline preload="none"></video>
        <div class="cutname">{ad} · {d}</div><div class="dls">{"".join(files)}</div>{thumbs_more(more)}</div></div>
      <div class="adtext">{khead(ad, "Video ad", plan_label(ad))}<h3>{esc(c["title"])}</h3>{whenline}
        {track(ad)}
        <p class="note">{esc(KIND[ad])}. Ad name <code>{ad}</code>, call to action Book now.</p>
        <details class="copybox"><summary>Copy to paste</summary><div class="twocol">{copy_field("Headline", c["headline"])}{copy_field("Description", c["description"])}</div>{text}</details>
      </div>
    </article>''')
    iron_statics = []
    for ad in ("IR1", "IR2"):
        c = ir[ad]
        iron_statics.append(static_tile(ad, c["title"], c["primary"], c["headline"], c["description"], simgs(idir, ad), "r4", svc="iron"))
    for ad in ("IR4", "IR5", "IR6"):
        c = ir2[ad]
        iron_statics.append(static_tile(ad, c["title"], c["short"], c["headline"], c["description"], simgs(i2dir, ad), "r5",
                                        extra=copy_field("Primary text (long)", c["long"], 6), svc="iron"))
    for name in ("COPY-IRON-R2.md", "GOOGLE-ADS-IRON.md", "COPY-IRON.md", "COPY-CYCLE.md", "GOOGLE-ADS-CYCLE.md"):   # linked from the sections
        put(os.path.join(STUDIO, "static", name), f"files/{name}")

    # ---------------- Cycle & Hormone Care, round 4 (Oct 28): Set 1 general (CA1-CA5 + the CC carousel), Set 2 by condition
    #                  (CP PMOS, CD PMDD, CE endometriosis), + Google search ad groups CG1-CG4 (Oct 22)
    cdir = os.path.join(sdir, "r9", "cycle")
    cyc = cycle_copy()
    COND = {"CP": "PMOS (formerly PCOS)", "CD": "PMDD", "CE": "Endometriosis"}
    tile = lambda ad, fmt: static_tile(ad, cyc[ad]["title"], cyc[ad]["primary"], cyc[ad]["headline"], cyc[ad]["description"],
                                       simgs(cdir, ad), "r9", svc="cycle", fmt=fmt)
    cycle_set1 = [tile(ad, "Single image ad") for ad in sorted(k for k in cyc if k.startswith("CA"))]
    cycle_set2 = [tile(ad, f"Single image ad · {COND[ad[:2]]}") for pre in ("CP", "CD", "CE") for ad in sorted(k for k in cyc if k.startswith(pre))]
    cc = cycle_carousel()
    nc = len(cc["cards"])
    cards = []
    for i, (cid, onimg, chead) in enumerate(cc["cards"], 1):
        src = os.path.join(sdir, "r9", "cycle-carousel", f"{cid}_card{i}_1x1.png")
        rel = put(src, f"static-ads/r9/{os.path.basename(src)}")
        zips["r9"].append((src, f"CC carousel/{os.path.basename(src)}"))
        th = thumb(src, f"static-ads/r9/thumbs/{cid}.jpg", 360)
        cards.append(f'<figure><img src="{th}" alt="{cid}" loading="lazy"><figcaption><span class="cardno">Card {i} of {nc}</span>'
                     f'<b>{cid}</b> · {esc(chead)}<div class="dls">{dl(rel, "Card", mb(src), True)}</div></figcaption></figure>')
    isnew, newpill, whenline = when("CC")
    n["cycle"] += 1
    cat("CC", f"Carousel, {nc} cards: " + cc["cards"][0][1], "cycle", "Carousel ad", "CC", f"static-ads/r9/thumbs/{cc['cards'][0][0]}.jpg")
    cycle_carousel_html = f'''
    <div class="group"><h3>Set 1 · Carousel</h3><span>One ad, not {nc} separate ones: in Ads Manager pick the Carousel format and add the cards in this order, each with its headline.</span></div>
    <article class="card carousel{" isnew" if isnew else ""}" id="CC">{khead(f"CC1–CC{nc}", f"Carousel ad · {nc} cards", plan_label("CC"))}<h3>Cycle &amp; Hormone Care carousel</h3>{whenline}{track("CC")}
      <div class="cards seq n{nc}">{"".join(cards)}</div><details class="copybox"><summary>Copy to paste</summary>{copy_field(f"Primary text (shared by all {nc} cards)", cc["primary"], 3)}</details></article>'''
    def gcard(gid, title, kws, hs, ds, pin, path, assets, svc):
        isnew, newpill, whenline = when(gid)
        n[svc] += 1
        cat(gid, title, svc, "Google search ad", gid, "", kind="google")
        return f'''
      <article class="card gad{" isnew" if isnew else ""}" id="{gid}">
        <div class="gadtop"><div>{khead(gid, "Google search ad", plan_label(gid))}<h4>{esc(title)}</h4>{whenline}{track(gid)}</div>
          <p class="note">One responsive search ad, named <code>{gid}-RSA</code>. {f"Pin “{esc(pin)}” to headline position 1. " if pin else ""}Display path <code>beoptimal.ca/{esc(path)}</code>. {len(hs)} headlines, {len(ds)} descriptions, {len(kws)} keywords.</p></div>
        <div class="gprev">
          <figure class="gdesk"><figcaption>Google on a computer</figcaption>{serp(hs, ds, path, assets)}</figure>
          <figure class="gmob"><figcaption>Google on a phone</figcaption><div class="phone">{serp(hs, ds, path, assets, mobile=True)}</div></figure>
        </div>
        <p class="gnote">A preview. Google mixes the {len(hs)} headlines and {len(ds)} descriptions, and may add callouts or a services line, so live ads vary.
          <b class="ok">Within Google's limits:</b> longest headline {max(map(len, hs))}/30 characters, longest description {max(map(len, ds))}/90.</p>
        <details class="more"><summary>Every headline and description, with its character count</summary>
          <ol class="glens">{"".join(f'<li><span>{esc(h)}</span><em>{len(h)}/30</em></li>' for h in hs)}</ol>
          <ol class="glens">{"".join(f'<li><span>{esc(d)}</span><em>{len(d)}/90</em></li>' for d in ds)}</ol></details>
        <details class="more"><summary>Copy to paste into Google Ads</summary>{copy_field("Headlines (one per line)", chr(10).join(hs), 8)}{copy_field("Descriptions", chr(10).join(ds), 4)}{copy_field("Keywords", chr(10).join(kws), 5)}</details>
      </article>'''

    gassets = google_assets()
    cycle_google = {"gen": [], "cond": []}
    for g in google_groups():
        cycle_google["gen" if g[0] in ("CG1", "CG2") else "cond"].append(gcard(*g, gassets, "cycle"))
    iron_assets = google_assets("GOOGLE-ADS-IRON.md")
    iron_google = [gcard(*g, iron_assets, "iron") for g in google_groups("GOOGLE-ADS-IRON.md")]
    th8 = open(os.path.join(STUDIO, "..", "optimal-content-library", "SHOTLIST.md")).read()
    th8 = th8[th8.index("**TH8"):th8.index("### Strongly want")].strip()
    open(os.path.join(HERE, "files", "TH8-iv-iron-shoot-script.md"), "w").write("# TH8 · IV iron · 30-second shoot script (Oct 19, 2026)\n\n" + th8 + "\n")

    # ---------------- Instagram posts (organic): 4:5 feed video (<10 MB upload copy) + 9:16 reel + covers + caption
    igu = os.path.join(STUDIO, "out", "ig-upload")
    ig_html = []
    for pid, folder, name, line, added, st in POSTS:
        out = os.path.join(STUDIO, "out", folder)
        feed, cov45 = os.path.join(igu, f"{pid}_feed_4x5.mp4"), os.path.join(igu, f"{pid}_cover_4x5.jpg")
        reel = next((os.path.join(out, f) for f in (f"{name}_FEED_Reel_9x16.mp4", f"{name}_IG_Tight_9x16.mp4", f"{name}_IG_Full_9x16.mp4",
                                                      f"{name}_Reel_9x16.mp4") if os.path.exists(os.path.join(out, f))), None)
        if not os.path.exists(feed):
            continue
        if pid.startswith("IRT"):
            m = re.search(rf"### {pid} · .*?\*\*Instagram caption \(organic, later\):\*\* (.*?)\n", iron2_doc, re.S)
            cap = m[1].strip() if m else ""
        else:
            m = re.search(rf"### {pid} caption\n(.*?)(?=\n### |\n---|\Z)", social, re.S)
            cap = m[1].strip() if m else ""
        prev = web_preview(feed, f"previews/ig/{pid}_4x5.mp4")
        cov_rel = put(cov45, f"files/IG_{pid}_cover_4x5.jpg") if os.path.exists(cov45) else prev[:-4] + ".jpg"
        files = [dl(stage(feed, f"IG_{pid}_feed_4x5.mp4"), "Feed post 4:5", mb(feed), True)]
        if reel:
            files.append(dl(stage(reel, f"IG_{pid}_reel_9x16.mp4"), "Reel 9:16", mb(reel)))
        if os.path.exists(cov45):
            files.append(dl(cov_rel, "Cover 4:5", mb(cov45)))
        isnew, newpill, whenline = when(pid, added)
        n["ig"] += 1
        if not any(e["code"] == pid for e in CATALOG):     # IRT1-4 are ads too: one tracker row each, already listed
            svc = "iron" if pid.startswith("IR") else "clinic" if pid in ("RB1", "CI1") else "menopause"
            cat(pid, line, svc, "Organic video", f"ig-{pid}", cov_rel, base=pid, kind="organic")
        ig_html.append(f'''
      <article class="card tile ig{" isnew" if isnew else ""}" id="ig-{pid}">
        <video src="{prev}" poster="{cov_rel}" controls playsinline preload="none"></video>
        <div class="tbody">{khead(pid, "Organic video", "also a paid ad" if pid.startswith("IRT") else "")}<h4>{esc(line)}</h4>{whenline}{track(pid)}
          <div class="dls">{"".join(files)}</div>
          <details class="more"><summary>Caption</summary>{copy_field("Caption", cap, 8)}</details>
        </div>
      </article>''')

    seen = set()
    ig_ads_html = []
    for e in CATALOG:
        base = e["code"].split("-")[0]
        if not e.get("organic_ok") or base in seen or base.startswith("IRT"):     # IRT1-4 already have organic cards above
            continue
        seen.add(base)
        ig_ads_html.append(f'''
      <article class="card tile ig adpost" id="post-{esc(base)}">
        <a href="#{esc(e["anchor"])}"><img src="{esc(e["thumb"])}" alt="" loading="lazy"></a>
        <div class="tbody">{khead(e["code"], "Paid ad", "also works as a post")}<h4>{esc(e["line"])}</h4>{track(e["code"])}
          <p class="note"><a href="#{esc(e["anchor"])}">Files and copy are on its ad card →</a></p></div>
      </article>''')

    # ---------------- zips (release assets), as before
    for key, fname, extra in (("r5", f"Optimal-IV-iron-ads-round-2_{TAG}.zip", [(os.path.join(STUDIO, "static/COPY-IRON-R2.md"), "COPY.md"),
                                                                                  (os.path.join(STUDIO, "static/GOOGLE-ADS-IRON.md"), "GOOGLE-ADS.md")]),
                              ("r1", f"Optimal-static-ads-round-1_{TAG}.zip", [(os.path.join(STUDIO, "static/COPY.md"), "COPY.md")]),
                              ("r2", f"Optimal-static-ads-round-2_{TAG}.zip", [(os.path.join(STUDIO, "static/COPY-R2.md"), "COPY.md")]),
                              ("r3", f"Optimal-static-ads-round-3_{TAG}.zip", [(os.path.join(STUDIO, "static/COPY-R3.md"), "COPY.md")]),
                              ("r4", f"Optimal-IV-iron-ads_{TAG}.zip", [(os.path.join(STUDIO, "static/COPY-IRON.md"), "COPY.md")]),
                              ("r9", f"Optimal-cycle-hormone-statics_{TAG}.zip", [(os.path.join(STUDIO, "static/COPY-CYCLE.md"), "COPY.md"),
                                                                                    (os.path.join(STUDIO, "static/GOOGLE-ADS-CYCLE.md"), "GOOGLE-ADS.md")])):
        zp = os.path.join(STAGE, fname)
        names = sorted(arc for _, arc in zips[key] + extra)
        stale = not os.path.exists(zp) or any(os.path.getmtime(src) > os.path.getmtime(zp) for src, _ in zips[key] + extra)
        if not stale:
            with zipfile.ZipFile(zp) as z:
                stale = sorted(z.namelist()) != names           # e.g. IR3 removed: rebuild even though nothing is newer
        if stale:
            with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
                for src, arc in zips[key] + extra:
                    z.write(src, arc)
    zl = [("Static round 1", f"Optimal-static-ads-round-1_{TAG}.zip"), ("Static round 2", f"Optimal-static-ads-round-2_{TAG}.zip"),
          ("Static round 3", f"Optimal-static-ads-round-3_{TAG}.zip"), ("IV iron round 1", f"Optimal-IV-iron-ads_{TAG}.zip"),
          ("IV iron round 2", f"Optimal-IV-iron-ads-round-2_{TAG}.zip"), ("Cycle & Hormone statics", f"Optimal-cycle-hormone-statics_{TAG}.zip")]
    zips_html = " ".join(f'<a href="{REL + f}" download>{esc(lbl)} · {mb(os.path.join(STAGE, f))}</a>' for lbl, f in zl)
    shutil.copy2(os.path.join(STUDIO, "brand/ds/assets/logos/OptimalLogo-Green.png"), os.path.join(HERE, "files", "logo.png"))
    Image.open(os.path.join(STUDIO, "brand/ds/assets/logos/optimal-symbol-green.png")).convert("RGBA").resize((36, 36), Image.LANCZOS).save(
        os.path.join(HERE, "files", "g-favicon.png"))

    # ---------------- what's new
    def chip(i):
        return f'<a href="#{i}">{esc(i[3:] if i.startswith("ig-") else SHOW_ID.get(i, i))}{" (post)" if i.startswith("ig-") else ""}</a>'
    days = [f'<div class="day{" latest" if d == LATEST else ""}"><div class="date">{fmt(d)}</div><div><p>{esc(t)}</p>'
            f'<div class="ids">{"".join(chip(i) for i in ids)}{"".join(f"<span class=gone>{g} removed</span>" for g in gone)}</div></div></div>'
            for d, t, ids, gone in NEWS]
    news = "".join(days[:3]) + f'<details class="older"><summary>Earlier updates ({len(days) - 3})</summary>{"".join(days[3:])}</details>'

    # ---------------- plan + rewrites (How to launch)
    thumbs, titles = {}, {}
    for vid, svc, folder, name, line, *rest in VIDEOS:
        thumbs[vid], titles[vid] = f"previews/{name}_Tight_9x16.jpg", line
    for ad, c in list(r1.items()) + list(r2.items()) + list(r3.items()):
        if ad in CUT:
            continue
        rk = "r1" if ad in r1 else "r2" if ad in r2 else "r3"
        new = RENAME.get(ad, ad)
        thumbs[new], titles[new] = f"static-ads/{rk}/thumbs/{new}.jpg", c["title"]
    for key in ("MC", "LC"):
        thumbs[key] = f"static-ads/r2/thumbs/{key}1.jpg"
        titles[key] = "Menopause carousel, 5 cards" if key == "MC" else "Longevity carousel, 5 cards"
    for k, *_ in REWRITES:
        thumbs.setdefault(k, f"static-ads/r2/thumbs/{k}.jpg")
    missing = [k for k in PLAN if not os.path.exists(os.path.join(HERE, thumbs.get(k, "-")))]
    assert not missing, f"plan thumbnails missing: {missing}"

    def setup(svc, audience):
        return (kv("Website URL", SERVICES[svc]["dest"], True) + kv("URL parameters", SERVICES[svc]["utm"], True)
                + kv("Call to action", "Book now") + kv("Audience", audience))
    IRON_UTM = "utm_source={{site_source_name}}&utm_medium=paid&utm_campaign={{campaign.id}}&utm_term={{adset.id}}&utm_content={{ad.id}}"
    iron_setup = (kv("Campaign", "Sales → website conversions, optimized for BookAppointmentSuccess")
                  + kv("Website URL", "https://www.beoptimal.ca/services/iron", True) + kv("Call to action", "Book now")
                  + kv("Ad sets", "One, images and videos together. Start with IR1, IR2, IRV1 and IRT1, then add one or two a week")
                  + kv("Audience", "Adults 25–64, about 40 km around Barrie, broad"))
    iron_howto = f'''
      <div class="twocol">
        <div>{copy_field("URL parameters", IRON_UTM, 2)}</div>
        <div><ul class="rules">
          <li><b>Before launch:</b> the IV iron page still shows “Save my founding spot”. Its buttons need to open booking first, so the page matches the ads. The Instant Form is retired.</li>
          <li><b>Judge on</b> cost per booked consult; for video, the 3-second hold and ThruPlay.</li>
          <li><b>Google Ads:</b> <a href="files/GOOGLE-ADS-IRON.md" target="_blank" rel="noopener">GOOGLE-ADS-IRON.md</a>, ready to build. Add the booking conversion first.</li>
          <li><b>All the copy:</b> <a href="files/COPY-IRON.md" target="_blank" rel="noopener">COPY-IRON.md</a> (IR1, IR2, IRV1) and <a href="files/COPY-IRON-R2.md" target="_blank" rel="noopener">COPY-IRON-R2.md</a> (the rest). Shoot script: <a href="files/TH8-iv-iron-shoot-script.md" target="_blank" rel="noopener">TH8</a>.</li>
        </ul></div>
      </div>'''

    # ---------------- the tracker: catalog (what exists) + last known statuses (what the sheet said at build time)
    posted = {pid: st.split(" ", 1)[1] for pid, *_, st in POSTS if st.startswith("posted")}
    for e in CATALOG:
        b = e["code"].split("-")[0]
        if b in IG_LINK:
            e["seed"] = dict(ig="Posted", ig_date=posted.get(b, "") + ", 2026", ig_link=f"https://www.instagram.com/reel/{IG_LINK[b]}/")
        elif b in IG_STATIC:
            e["seed"] = dict(ig="Posted", ig_date=IG_STATIC[b][1] + ", 2026", ig_link=f"https://www.instagram.com/p/{IG_STATIC[b][0]}/")
        elif b in posted:
            e["seed"] = dict(ig="Posted", ig_date=posted[b] + ", 2026")
    json.dump(CATALOG, open(os.path.join(HERE, "catalog.json"), "w"), indent=1, ensure_ascii=False)
    snaps = {}
    for tab, fname, head in (("Tracker", "tracker-snapshot.csv", "Code"), ("Sync%20log", "sync-log-snapshot.csv", "When")):
        path = os.path.join(HERE, fname)
        try:
            text = urllib.request.urlopen(TRACKER_BASE + tab, timeout=15).read().decode("utf-8")
            if text.lstrip('"').startswith(head):
                open(path, "w").write(text)
        except Exception as e:
            print(f"tracker tab {tab} not readable at build time, keeping the last snapshot:", e)
        snaps[fname] = open(path).read() if os.path.exists(path) else ""
    snap_path = os.path.join(HERE, "tracker-snapshot.csv")
    snap = snaps["tracker-snapshot.csv"]
    snap_at = time.strftime("%b %-d, %Y %-I:%M %p", time.localtime(os.path.getmtime(snap_path))) if snap else ""
    jsdump = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")

    page = TEMPLATE
    for k, v in {
        "CATALOG_JSON": jsdump(CATALOG), "SNAPSHOT_JSON": jsdump(dict(csv=snap, log=snaps["sync-log-snapshot.csv"], at=snap_at)),
        "TRACKER_EDIT": TRACKER_EDIT, "TRACKER_BASE": TRACKER_BASE, "TRACKER_KPI": TRACKER_KPI, "N_ALL": str(len(CATALOG)),
        "UPDATED": UPDATED, "TAG": TAG, "RELEASE": f"https://github.com/{REPO}/releases/tag/{TAG}", "ZIPS": zips_html,
        "WHATSNEW": news, "N_MENO": str(n["menopause"]), "N_LONG": str(n["longevity"]), "N_IRON": str(n["iron"]), "N_IG": str(n["ig"]),
        "MENO_SETUP": setup("menopause", "Women 35–60, about 40 km around Barrie, broad"),
        "CYCLE_SETUP": (kv("Website URL", SERVICES["cycle"]["dest"], True) + kv("URL parameters", SERVICES["cycle"]["utm"], True)
                        + kv("Call to action", "Learn more · Book now on CV3") + kv("Ad sets", "Set 1 general: CV, CA, CC · Set 2 by condition: CP, CD, CE")
                        + kv("Audience", "Women 18–45, about 40 km around Barrie, broad")),
        "CYCLE_VIDEOS": "".join(vids["cycle"]), "N_CYCLE": str(n["cycle"]),
        "CYCLE_SET1": "".join(cycle_set1), "CYCLE_SET2": "".join(cycle_set2),
        "CYCLE_GOOGLE_GEN": "".join(cycle_google["gen"]), "CYCLE_GOOGLE_COND": "".join(cycle_google["cond"]), "CYCLE_CAROUSEL": cycle_carousel_html,
        "LONG_SETUP": setup("longevity", "Adults 35–70, about 40 km around Barrie, broad"),
        "IRON_SETUP": iron_setup, "IRON_HOWTO": iron_howto,
        "MENO_VIDEOS": "".join(vids["menopause"]), "LONG_VIDEOS": "".join(vids["longevity"]),
        "MENO_STATICS": "".join(statics["menopause"]), "LONG_STATICS": "".join(statics["longevity"]),
        "MENO_CAROUSEL": carousels["menopause"], "LONG_CAROUSEL": carousels["longevity"],
        "IRON_VIDEOS": "".join(iron_videos), "IRON_STATICS": "".join(iron_statics), "IG_POSTS": "".join(ig_html),
        "IG_ADS": "".join(ig_ads_html), "IRON_GOOGLE": "".join(iron_google),
        "CHECKLIST": CHECKLIST, "PLAN": plan_html(thumbs, titles), "REWRITES": rewrites_html(thumbs),
    }.items():
        page = page.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z0-9_]+\}\}", page)
    assert not left, f"unfilled placeholders: {left}"
    open(os.path.join(HERE, "index.html"), "w").write(page)
    print(f"built: menopause {n['menopause']}, longevity {n['longevity']}, cycle {n['cycle']}, iron {n['iron']}, instagram {n['ig']}; "
          f"release staging {sum(os.path.getsize(os.path.join(STAGE, f)) for f in os.listdir(STAGE)) / 1e6:.0f} MB")


def publish():
    run = lambda *a: subprocess.run(a, check=True, cwd=HERE)
    assets = sorted(os.path.join(STAGE, f) for f in os.listdir(STAGE))
    if subprocess.run(["gh", "release", "view", TAG, "-R", REPO], capture_output=True).returncode != 0:
        run("gh", "release", "create", TAG, "-R", REPO, "--title", f"Ads · {ROUND}", "--notes",
            f"Full-quality files for the {ROUND} ad round. Browse and copy the ad text at "
            f"https://optimal-research-team.github.io/optimal-ad-handoff/")
    have = {a["name"]: a["size"] for a in json.loads(subprocess.run(
        ["gh", "release", "view", TAG, "-R", REPO, "--json", "assets"], capture_output=True, text=True).stdout)["assets"]}
    todo = [p for p in assets if have.get(os.path.basename(p)) != os.path.getsize(p)]   # skip files already up
    if todo:
        run("gh", "release", "upload", TAG, "-R", REPO, "--clobber", *todo)
    run("git", "add", "-A")
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=HERE).returncode:
        run("git", "commit", "-q", "-m", f"Hand-off site: ads updated {UPDATED}\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
    run("git", "push", "-q", "origin", "main")


TEMPLATE = open(os.path.join(HERE, "template.html")).read()

if __name__ == "__main__":
    build()
    if "--publish" in sys.argv:
        publish()
