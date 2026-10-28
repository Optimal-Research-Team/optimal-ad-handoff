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
TRACKER_CSV = f"https://docs.google.com/spreadsheets/d/{TRACKER_ID}/gviz/tq?tqx=out:csv&sheet=Tracker"
# Meta's AI label ("AI info"): the copy docs say which ads use AI imagery or AI motion
AI_ON = set(("MB1 MB2 MB3 MB4 MB5 MB6 LB1 LB2 LB3 LB4 LB5 LB6 MC LC MA1 MA2 LA1 LA2 MV2 CV2 "        # round 2 + 3, two videos
             "IR1 IR2 IRV1 IR4 IR5 IR6 IRM1 IRM2 IRV2 IRV3 IRT1 IRT2 IRT3 IRT4 "                     # IV iron: every ad
             "CA2 CA3 CC CP1 CE1 CE2").split())                                                     # cycle round 4 engravings
CATALOG = []   # one entry per tracker row, filled while the page is built


def cat(code, line, svc, fmt, anchor, thumb, base=None, kind="ad"):
    b = base or code
    CATALOG.append(dict(code=code, line=re.sub(r"[*{}]", "", line).replace("|", " "), svc=svc, fmt=fmt, anchor=anchor,
                        thumb=thumb, plan=plan_label(b), ai=b in AI_ON, added=ADDED.get(b, ""), kind=kind))


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
WAITING = {k: "Waiting on the landing page" for k in ("CV1", "CV2", "CV3", "CC", "CG1", "CG2", "CG3", "CG4") + CYCLE_R4}
# /services/cycle-and-hormone-care 404s (Oct 22)
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
    # menopause
    "M3":  ("now", 1, "Price up front, qualifies the booking · price card"),
    "MV1": ("now", 2, "Emotional hook · video"),
    "MV3": ("next", None, "A/B vs MV1: the NP on camera, same offer · video"),
    "MV2": ("next", None, "NP explains the full-hour first visit · video"),
    "MB1": ("now", 3, "Relatable moment · photo"),
    "MB5": ("now", 4, "Access, no referral · clinic photo"),
    "MB2": ("now", 5, "Symptom awareness · photo"),
    "MC":  ("now", 6, "How it works · carousel"),
    "M2":  ("next", None, "60-minute first visit · big number"),
    "M1":  ("next", None, "Symptom list · education"),
    "MB4": ("next", None, "Hot flashes at work · photo"),
    "MB3": ("next", None, "NP-led, in Barrie · photo"),
    "M6":  ("twin", "MB1", "3 a.m. · night photo"),
    "M4":  ("twin", "MB5", "No referral · photo + capsule"),
    "M5":  ("twin", "MC", "How it works · step diagram"),
    "MB6": ("twin", "M2", "60-minute visit · consult photo"),
    "MA1": ("twin", "M3", "$895 + HST · engraving"),
    "MA2": ("next", None, "Midlife, planned for · botanical plate"),
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
    ("MA1", "Three months, one Nurse Practitioner, one price: $895.", "Three months, one Nurse Practitioner, one price: $895 + HST.", "Matches the price card and the consent form, so there's no surprise at the first visit."),
    ("LA2", "Normal is a range. We talk about where you sit in it.", "Normal is a range, and we look at where you sit in it.", "Same idea, held to one sentence."),
    ("MC1", "It starts with a free 15-minute call.", "Menopause care in Barrie starts with a free 15-minute call.", "Card 1 has to say who and where, or nobody swipes."),
    ("MC4", "You get a written treatment plan.", "You get a written plan and the same NP every visit.", "Adds continuity: the same person at every visit, so the plan comes with someone who knows the history."),
    ("MC5", "Book your free call at beoptimal.ca.", "No referral needed: book your free call at beoptimal.ca.", "Removes the last objection right at the call to action."),
    ("LC1", "Here’s what $1,495 a year includes.", "Here’s everything $1,495 a year gets you.", "“Gets you” is about the reader, not the product."),
    ("LC5", "Book a free intro call at beoptimal.ca.", "Start with a free 15-minute call, no commitment.", "Risk reversal: free, short and no strings."),
]

# IV iron (Oct 14, 2026): pre-launch, founding waitlist only, on a Meta Instant Form (no landing page yet).
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
        m = re.match(r"(CG\d) · ([^\n]+)", g)
        if not m:
            continue
        kw = re.findall(r"^- `(.*?)`", g.split("**Headlines")[0], re.M)
        clean = lambda l: re.sub(r"\s*\*\(.*?\)\*", "", re.sub(r"^\d+\.\s*", "", l)).strip()
        hs = [clean(l) for l in re.search(r"\*\*Headlines \(15\):\*\*\n(.*?)\n\n", g, re.S)[1].splitlines()]
        ds = [clean(l) for l in re.search(r"\*\*Descriptions \(4\):\*\*\n(.*?)(?:\n\n|\Z)", g, re.S)[1].splitlines()]
        pin = re.search(r"^1\. (.*?) \*\(pin", g, re.M)
        out.append((m[1], m[2], kw, hs, ds, pin[1] if pin else None))
    return out


# ------------------------------------------------------------------ html pieces
def copy_field(label, text, rows=None):
    t = esc(text)
    body = f'<textarea readonly rows="{rows}">{t}</textarea>' if rows else f'<div class="val">{t}</div>'
    return (f'<div class="field"><div class="flabel">{esc(label)}<button class="copy" data-copy="{t}">Copy</button></div>'
            f'{body}</div>')


def ad_names(vid, cuts):
    if len(cuts) == 1:
        return f"Ad name <code>{vid}-{cuts[0][0]}</code>."
    return (f"Two ads: <code>{vid}-T</code> (Tight, about MV1's length: the NP-vs-care-coordinator test against "
            f"<code>MV1-T</code>, same end card, offer and page) and <code>{vid}-F</code> (Flow, runs past 30 s: the length "
            f"test against {vid}-T). Same ad set, Meta A/B test, equal budgets; judge on cost per booked intro call.")


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
UPDATED = "Oct 28, 2026"
LATEST = "2026-10-28"
D12, D13, D14, D15, D19, D20, D21, D22, D26, D28 = ("2026-10-12", "2026-10-13", "2026-10-14", "2026-10-15", "2026-10-19", "2026-10-20",
                                                    "2026-10-21", "2026-10-22", "2026-10-26", "2026-10-28")
ADDED = {**{k: D12 for k in ("M1 M2 M3 M4 M5 M6 L1 L2 L3 L4 L5 L6 MB1 MB2 MB3 MB4 MB5 MB6 LB1 LB2 LB3 LB4 LB5 LB6 "
                             "MC LC LV1 LV2 MV1").split()},
         **{k: D13 for k in ("MA1", "MA2", "LA1", "LA2")},
         **{k: D14 for k in ("IR1", "IR2", "IRV1")},
         "LV3": D15,
         **{k: D19 for k in ("IR4", "IR5", "IR6", "IRM1", "IRM2", "IRV2", "IRV3")},
         **{k: D20 for k in ("IRT1", "IRT2", "IRT3", "IRT4", "MV2", "MV3")},
         **{k: D22 for k in ("CV1", "CV2", "CV3", "CC", "CG1", "CG2", "CG3", "CG4")},
         **{k: D28 for k in CYCLE_R4}}
CHANGED = {"IR1": (D20, "new image and headline"), "IR2": (D20, "new image: the website hero"),
           "IRV1": (D20, "rebuilt from the website hero, animated"),
           "MV2": (D21, "blood-draw and body-scan pictures; softer opening"),
           "MV3": (D21, "hormone-levels chart from the menopause page; softer opening"),
           "CB2": (D21, "pause at 0:42 cut; softer opening"),
           "CB1": (D21, "opening shot and the 0:30 graphic cut"),
           **{k: (D21, "softer opening (room tone, not silence)") for k in ("MI1", "MI2", "MI3")}}
CHANGED["MI2"] = (D26, "new cover: Chantelle smiling, not mid-word")
CHANGED["CC"] = (D28, "redone as 6 cards, one symptom group per card")
REMOVED = {"IR3": D20}
SHORT = {"9x16": "9:16", "1x1": "1:1", "1-91x1": "1.91:1"}
NEWS = [  # (date, what happened, ids that link to cards, ids removed)
    (D28, "Cycle & Hormone Care statics redone in two sets. Set 1 (general) covers every symptom the program looks at: five "
          "single-image ads (CA1–CA5) and a 6-card carousel (CC1–CC6) with one symptom group per card. Set 2 (by condition) "
          "has two ads each for PMOS (formerly PCOS), PMDD and endometriosis (CP, CD, CE). They describe the signs and never "
          "ask \u201cDo you have…?\u201d, which Meta rejects. The old singles CS3–CS6 are retired. Also new: the Summary tab, one table of "
          "every ad and post showing where each one is live (Meta, Instagram, Facebook, Google), read live from the shared "
          "tracker sheet.", ["CA1", "CA2", "CA3", "CA4", "CA5", "CC", "CP1", "CP2", "CD1", "CD2", "CE1", "CE2"], ["CS3–CS6"]),
    (D26, "Instagram check: nothing new has gone up since Oct 24. MI2 (brain fog) was taken down for its cover, which caught "
          "Chantelle mid-word, and reposted on Oct 26 with a new cover (a smiling frame). MA2 is live as an organic feed post (since Oct 23), and its card "
          "now says so. Two drawn 3-D equipment reels went up on Oct 24 (the InBody 580 and the KICKR BIKE); they aren't ads, so "
          "they have no cards here. New rule for organic posts (Peter, Oct 24): nothing that needs Meta's AI label goes on "
          "Instagram or Facebook.", ["ig-MI2", "MA2"], []),
    (D22, "New service: Cycle & Hormone Care. Cheryl's three video ads (labelled with the program from the first frame), four "
          "single statics that each stand alone, one 5-card carousel that tells the story in order (hook, symptoms can "
          "connect, how we look, 12 weeks, free Cycle Check), and a Google search campaign in four ad groups. Hold everything "
          "until the Cycle & Hormone Care page is live (the URL 404s today).",
     ["CV1", "CV2", "CV3", "CC", "CS3", "CS4", "CS5", "CS6", "CG1", "CG2", "CG3", "CG4"], []),
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
# organic Instagram posts (not ads): id, folder in meta-ad-studio/out, render name, line, added, status
# static ads that also went up on Instagram as organic feed posts: id -> (post shortcode, date)
IG_STATIC = {"MA2": ("De2kqQAFkhP", "Oct 23")}
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
    ("IRT3", "iron-three-things", "IronThreeThings", "3 things about IV iron.", D20, "posted Oct 21"),
    ("IRT4", "iron-what-it-looks-like", "IronWhatItLooksLike", "What IV iron actually looks like.", D20, "posted Oct 21"),
    ("RB1", "rubeana-bio", "RubeanaBio", "Meet Rubeana, our Clinical Director.", D15, "posted Oct 15"),
    ("CI1", "cholesterol-info", "CholesterolInfo", "Cholesterol, explained: HDL, LDL, Lp(a) and ApoB.", D15, "posted Oct 15"),
]


def fmt(d):
    m = {"10": "Oct", "11": "Nov", "09": "Sep"}[d[5:7]]
    return f"{m} {int(d[8:])}"


def when(ad, added=None):
    """(is new on the latest date, pills html, 'Added … · updated …' line)"""
    a = added or ADDED.get(ad)
    u = CHANGED.get(ad) or ((D19, "re-made in Meta's 3 ratios") if a and a < D19 else None)
    new = "New" if a == LATEST else ("Updated" if u and u[0] == LATEST else "")
    line = (f"Added {fmt(a)}" if a else "") + (f" · updated {fmt(u[0])}: {u[1]}" if u else "")
    if new:
        line = line.replace(f"{fmt(LATEST)}", f"<b>{fmt(LATEST)}</b>")
    return bool(new), (f'<span class="pill new">{new}</span>' if new else ""), f'<span class="when">{line}</span>'


def status(ad):
    if ad in WAITING:
        return f'<span class="pill hold">{esc(WAITING[ad])}</span>'
    if ad in IRON:
        return f'<span class="pill now">{esc(IRON[ad][1])}</span>'
    st, x, _ = PLAN.get(ad, (None, None, None))
    if st == "now":
        return f'<span class="pill now">Test now · #{x}</span>'
    if st == "next":
        return '<span class="pill next">Next up</span>'
    if st == "twin":
        return f'<span class="pill twin">Twin of {SHOW_ID.get(x, x)}</span>'
    return ""


def plan_label(ad):
    """the plan column, as plain text"""
    if ad in WAITING:
        return "Hold: page not live"
    if ad in IRON:
        return IRON[ad][1].split(" · cleared")[0]
    st, x, _ = PLAN.get(ad, (None, None, None))
    return {"now": f"Test now #{x}", "next": "Next up", "twin": f"Twin of {SHOW_ID.get(x, x)}"}.get(st, "")


def order(ad):
    st, x, _ = PLAN.get(ad, (None, None, None))
    return ({"now": 0, "next": 1, "twin": 2}.get(st, 3), x if st == "now" else 0, ad)


def kv(k, v, copy=False):
    btn = f'<button class="copy" data-copy="{esc(v)}">Copy</button>' if copy else ""
    return f'<div class="kv"><div class="k">{esc(k)}{btn}</div><div class="v">{esc(v)}</div></div>'


CHECKLIST = '''
  <label class="check"><input type="checkbox" data-k="g-404"><span><b>Pause the three old menopause statics</b> that link to beoptimal.ca/womens-health (a 404).
    <small>Ad Library IDs 4548870122052378, 1707193563843938, 1436333148369495.</small></span></label>
  <label class="check"><input type="checkbox" data-k="g-old"><span><b>Pause the older live ads</b> in the same campaigns so the test isn't diluted.
    <small>3267720843438130 (primary care intro), 28548023041524231 (menopause info call).</small></span></label>
  <label class="check"><input type="checkbox" data-k="g-sets"><span><b>One ad set per service</b> (Menopause, Longevity membership): broad audience, Advantage+ placements, Landing page views.</span></label>
  <label class="check"><input type="checkbox" data-k="g-m"><span><b>Upload the Menopause Test now ads</b> in rank order: M3, MV1-T, MB1, MB5, MB2, MC.</span></label>
  <label class="check"><input type="checkbox" data-k="g-l"><span><b>Upload the Longevity Test now ads</b> in rank order: LV1-T, L1, L2, LB1, LB2, LB3.</span></label>
  <label class="check"><input type="checkbox" data-k="g-ab"><span><b>Set up the Chantelle vs Cheryl test:</b> MV1-T against MV3-T as a Meta A/B test (equal budgets).</span></label>
  <label class="check"><input type="checkbox" data-k="g-ai"><span><b>Turn on Meta's AI label</b> for every round 2 and round 3 ad, CV2 and MV2, and wherever an IV iron card says so.</span></label>
  <label class="check"><input type="checkbox" data-k="g-cv"><span><b>Cycle & Hormone Care (CV1–CV3, CA1–CA5, CC, CP/CD/CE, CG1–CG4):</b> launch only once beoptimal.ca/services/cycle-and-hormone-care is live. Meta: two ad sets, women 18–45: Set 1 (general: CA, CC, CV) and Set 2 (by condition: CP, CD, CE). AI label on CV2, CA2, CA3, the CC carousel, CP1, CE1 and CE2. Google: build from GOOGLE-ADS-CYCLE.md (CHC campaign).</span></label>
  <label class="check"><input type="checkbox" data-k="g-track"><span><b>Mark it in the tracker</b> when an ad goes into Ads Manager, goes live, or is paused: one row per ad name, in the Google Sheet linked from the Summary tab. The page reads it live.</span></label>
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
      <div class="adtext">{status(vid)} {newpill}<h3><span class="id">{vid}</span>{esc(line)}</h3>{whenline}
        {track(*(f"{vid}-{k}" for k, _ in cuts))}
        <p class="note">{ad_names(vid, cuts)} Upload the 1:1, 9:16 and 1.91:1 files of a cut as one ad.</p>
        {copy_field("Primary text (short)", c["short"], 3)}{copy_field("Primary text (long)", c["long"], 7)}
        <div class="twocol">{copy_field("Headline", c["headline"])}{copy_field("Description", c["description"])}</div>{alt}
      </div>
    </article>''')

    # ---------------- static ads
    def static_tile(ad, title, primary, headline, description, imgs, round_key, extra="", svc=None, fmt=""):
        files = []
        for label, src in imgs:
            rel = put(src, f"static-ads/{round_key}/{os.path.basename(src)}")
            files.append(dl(rel, label.split(" ")[0], mb(src), primary=label.startswith(("1:1", "4:5"))))
            zips[round_key].append((src, os.path.basename(src)))
        th = thumb(imgs[0][1], f"static-ads/{round_key}/thumbs/{ad}.jpg")
        isnew, newpill, whenline = when(ad)
        desc = copy_field("Description", description) if description else ""
        ai = f'<span class="when">Meta AI label: <b class="ai">{"on" if ad in AI_ON else "off"}</b></span>'
        if svc:
            n[svc] += 1
            cat(ad, title, svc, "Image ad", ad, th)
        return f'''
      <article class="card tile{" isnew" if isnew else ""}" id="{ad}">
        <img src="{th}" alt="{esc(ad)}" loading="lazy">
        <div class="tbody"><div>{f'<span class="pill fmt">{esc(fmt)}</span> ' if fmt else ""}{status(ad)} {newpill}</div><h4><span class="id">{ad}</span>{esc(title)}</h4>{whenline}{ai}
          {track(ad)}
          <div class="dls">{"".join(files)}</div>
          <details class="more"><summary>Ad copy</summary>{copy_field("Primary text", primary, 4)}{copy_field("Headline", headline)}{desc}{extra}</details>
        </div>
      </article>'''

    sdir = os.path.join(STUDIO, "static/out")
    statics = {"menopause": [], "longevity": []}
    rows = []
    for ad, c in r1.items():
        rows.append((ad, c["title"], c["primary"], c["headline"], c["description"],
                     simgs(os.path.join(sdir, "meno" if ad[0] == "M" else "long"), ad), "r1"))
    for ad, c in r2.items():
        rows.append((ad, c["title"], c["primary"], c["headline"], None,
                     simgs(os.path.join(sdir, "r2", "meno" if ad[0] == "M" else "long"), ad), "r2"))
    for ad, c in r3.items():
        rows.append((ad, c["title"], c["primary"], c["headline"], c["description"],
                     simgs(os.path.join(sdir, "r3", "meno" if ad[0] == "M" else "long"), ad), "r3"))
    for row in sorted(rows, key=lambda r: order(r[0])):
        svc = "menopause" if row[0][0] == "M" else "longevity"
        statics[svc].append(static_tile(*row, svc=svc))

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
    <div class="group"><h3>Carousel</h3><span>Five 1:1 cards, uploaded as one carousel ad.</span></div>
    <article class="card carousel" id="{key}">{status(key)} {newpill}<h3 style="margin-top:6px"><span class="id">{key}1–{key}5</span>{SERVICES[svc]["name"]} carousel</h3>{whenline}{track(key)}
      <div class="cards">{"".join(cards)}</div>{copy_field("Primary text", car[key]["primary"], 2)}</article>'''

    # ---------------- IV iron: videos (talking heads, the hero film, motion, films) + statics. IR3 removed Oct 20 (Peter).
    idir, i2dir = os.path.join(sdir, "r4", "iron"), os.path.join(sdir, "r5", "iron")
    KIND = {"IRT1": "Talking head · Cheryl in our lounge · captions + engraving cards", "IRT2": "Talking head · Cheryl · symptom chips + cards",
            "IRT3": "Talking head · Cheryl · three numbered points", "IRT4": "Talking head · Cheryl · five numbered steps",
            "IRV1": "The IV iron page's hero, animated (close-up only), then the end card · silent · AI label on",
            "IRV2": "Film · Maeve voiceover · our real waiting lounge and reception + still lifes · AI label on",
            "IRV3": "Film · Maeve voiceover · home still lifes + our real waiting lounge · AI label on",
            "IRM1": "HyperFrames motion · silent · drawn graphics only", "IRM2": "HyperFrames motion · silent · the offer stack"}
    iron_videos = []
    for ad in ("IRT1", "IRT2", "IRT3", "IRT4", "IRV1", "IRV2", "IRV3", "IRM1", "IRM2"):
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
      <div class="adtext">{status(ad)} {newpill}<h3><span class="id">{ad}</span>{esc(c["title"])}</h3>{whenline}
        {track(ad)}
        <p class="note">{esc(KIND[ad])}. Ad name <code>{ad}</code>. CTA Sign up.</p>
        {text}<div class="twocol">{copy_field("Headline", c["headline"])}{copy_field("Description", c["description"])}</div>
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
    for name in ("COPY-IRON-R2.md", "GOOGLE-ADS-IRON.md", "COPY-IRON.md", "COPY-CYCLE.md", "GOOGLE-ADS-CYCLE.md"):
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
    <div class="group"><h3>Set 1 · Carousel ad: 1 ad, {nc} cards</h3><span>These {nc} are NOT separate ads. In Ads Manager pick the <b>Carousel</b> format and add the cards in this order (1 → {nc}), each with its card headline. The primary text is shared. Every card shows a Stories-style progress bar, and card 1 says "Swipe". AI label on.</span></div>
    <article class="card carousel{" isnew" if isnew else ""}" id="CC"><span class="pill fmt">Carousel · 1 ad · {nc} cards</span> {status("CC")} {newpill}<h3 style="margin-top:6px"><span class="id">CC1–CC{nc}</span>Cycle &amp; Hormone Care carousel</h3>{whenline}{track("CC")}
      <div class="cards seq n{nc}">{"".join(cards)}</div>{copy_field(f"Primary text (shared by all {nc} cards)", cc["primary"], 3)}</article>'''
    cycle_google = []
    for gid, title, kws, hs, ds, pin in google_groups():
        isnew, newpill, whenline = when(gid)
        n["cycle"] += 1
        cat(gid, title, "cycle", "Google search ad", gid, "", kind="google")
        cycle_google.append(f'''
      <article class="card tile{" isnew" if isnew else ""}" id="{gid}">
        <div class="tbody"><div>{status(gid)} {newpill}</div><h4><span class="id">{gid}</span>{esc(title)}</h4>{whenline}{track(gid)}
          <p class="note">One responsive search ad, named <code>{gid}-RSA</code>. {f"Pin “{esc(pin)}” to headline position 1. " if pin else ""}{len(hs)} headlines, {len(ds)} descriptions, {len(kws)} keywords.</p>
          <details class="more"><summary>Headlines, descriptions, keywords</summary>{copy_field("Headlines (one per line)", chr(10).join(hs), 8)}{copy_field("Descriptions", chr(10).join(ds), 4)}{copy_field("Keywords", chr(10).join(kws), 5)}</details>
        </div>
      </article>''')
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
        <div class="tbody"><div><span class="pill fmt">Organic post</span> {newpill}</div><h4><span class="id">{pid}</span>{esc(line)}</h4>{whenline}{track(pid)}
          <div class="dls">{"".join(files)}</div>
          <details class="more"><summary>Caption</summary>{copy_field("Caption", cap, 8)}</details>
        </div>
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
        rk = "r1" if ad in r1 else "r2" if ad in r2 else "r3"
        thumbs[ad], titles[ad] = f"static-ads/{rk}/thumbs/{ad}.jpg", c["title"]
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
    iron_setup = (kv("Campaign", "Leads → Instant form (\"Join the IV iron founding waitlist\")") + kv("Call to action", "Sign up")
                  + kv("Ad sets", "Two: Statics and Video, $15–20 a day each, 7 days hands off")
                  + kv("Audience", "Adults 25–64, about 40 km around Barrie, broad"))
    iron_howto = f'''
      <div class="twocol">
        <div>{copy_field("Instant Form intro", "IV iron is coming to Optimal in Barrie. Join the founding waitlist for first access, in signup order, and founding pricing. No referral needed.", 3)}
          <div class="field"><div class="flabel">Questions</div><div class="val">First name, email, phone (prefilled), plus one multiple-choice question: "Do you have private or workplace drug coverage?" Yes / No / Not sure. No health questions.</div></div>
          {copy_field("Privacy policy", "https://www.beoptimal.ca/privacy")}
          {copy_field("Thank-you screen", "You're on the list. We'll email you when booking opens. Questions? Call (437) 370-0291.", 2)}</div>
        <div><ul class="rules">
          <li><b>Judge on</b> cost per signup and the share answering "Yes" on drug coverage; for video, the 3-second hold and ThruPlay.</li>
          <li><b>Download the leads</b> every few days: founding access goes in signup order.</li>
          <li><b>The page is live:</b> beoptimal.ca/iron (redirects to /services/iron). A second ad set can test it as a website destination; keep the Instant Form as the default.</li>
          <li><b>Google Ads:</b> <a href="files/GOOGLE-ADS-IRON.md" target="_blank" rel="noopener">GOOGLE-ADS-IRON.md</a>, ready to build. Add a Google Ads conversion on the waitlist submit first.</li>
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
    snap_path = os.path.join(HERE, "tracker-snapshot.csv")
    try:
        csv_text = urllib.request.urlopen(TRACKER_CSV, timeout=15).read().decode("utf-8")
        if csv_text.lstrip('"').startswith("Code"):
            open(snap_path, "w").write(csv_text)
    except Exception as e:
        print("tracker not readable at build time, keeping the last snapshot:", e)
    snap = open(snap_path).read() if os.path.exists(snap_path) else ""
    snap_at = time.strftime("%b %-d, %Y %-I:%M %p", time.localtime(os.path.getmtime(snap_path))) if snap else ""
    jsdump = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")

    page = TEMPLATE
    for k, v in {
        "CATALOG_JSON": jsdump(CATALOG), "SNAPSHOT_JSON": jsdump(dict(csv=snap, at=snap_at)),
        "TRACKER_EDIT": TRACKER_EDIT, "TRACKER_CSV": TRACKER_CSV, "N_ALL": str(len(CATALOG)),
        "UPDATED": UPDATED, "TAG": TAG, "RELEASE": f"https://github.com/{REPO}/releases/tag/{TAG}", "ZIPS": zips_html,
        "WHATSNEW": news, "N_MENO": str(n["menopause"]), "N_LONG": str(n["longevity"]), "N_IRON": str(n["iron"]), "N_IG": str(n["ig"]),
        "MENO_SETUP": setup("menopause", "Women 35–60, about 40 km around Barrie, broad"),
        "CYCLE_SETUP": (kv("Website URL", SERVICES["cycle"]["dest"], True) + kv("URL parameters", SERVICES["cycle"]["utm"], True)
                        + kv("Call to action", "Learn more · Book now on CV3") + kv("Ad sets", "Set 1 general: CV, CA, CC · Set 2 by condition: CP, CD, CE")
                        + kv("Audience", "Women 18–45, about 40 km around Barrie, broad")),
        "CYCLE_VIDEOS": "".join(vids["cycle"]), "N_CYCLE": str(n["cycle"]),
        "CYCLE_SET1": "".join(cycle_set1), "CYCLE_SET2": "".join(cycle_set2), "CYCLE_GOOGLE": "".join(cycle_google), "CYCLE_CAROUSEL": cycle_carousel_html,
        "LONG_SETUP": setup("longevity", "Adults 35–70, about 40 km around Barrie, broad"),
        "IRON_SETUP": iron_setup, "IRON_HOWTO": iron_howto,
        "MENO_VIDEOS": "".join(vids["menopause"]), "LONG_VIDEOS": "".join(vids["longevity"]),
        "MENO_STATICS": "".join(statics["menopause"]), "LONG_STATICS": "".join(statics["longevity"]),
        "MENO_CAROUSEL": carousels["menopause"], "LONG_CAROUSEL": carousels["longevity"],
        "IRON_VIDEOS": "".join(iron_videos), "IRON_STATICS": "".join(iron_statics), "IG_POSTS": "".join(ig_html),
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
