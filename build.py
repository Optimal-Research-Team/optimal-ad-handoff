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
import zipfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.join(HERE, "..", "meta-ad-studio")
REPO = "Optimal-Research-Team/optimal-ad-handoff"
TAG = "2026-10-12"
ROUND = "October 12–13, 2026"
REL = f"https://github.com/{REPO}/releases/download/{TAG}/"
STAGE = os.path.join(HERE, "release")          # git-ignored: what gets uploaded to the release

SERVICES = {
    "longevity": dict(name="Longevity membership", dest="https://www.beoptimal.ca/membership",
                      utm="utm_source={{site_source_name}}&utm_medium=paid&utm_campaign={{campaign.id}}&utm_term={{adset.id}}&utm_content={{ad.id}}"),
    "menopause": dict(name="Menopause", dest="https://www.beoptimal.ca/services/menopause-and-perimenopause-care",
                      utm="utm_source={{site_source_name}}&utm_medium=paid&utm_campaign={{campaign.id}}&utm_term={{adset.id}}&utm_content={{ad.id}}"),
}
VIDEOS = [  # id, service, folder in meta-ad-studio/out, render name, the line on screen
    ("LV1", "longevity", "longevity-core-v2", "LongevityCore", "3 things to know before you book."),
    ("LV2", "longevity", "longevity-ad2", "LongevityFullHour", "A full hour. Every year."),
    ("MV1", "menopause", "menopause-ad1", "MenopauseMyself", "“I just don’t feel like myself.”"),
    ("LV3", "longevity", "health-optimizer", "LongevityOptimize", "An hour with an NP who listens."),   # Oct 15, Rubeana
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
    "IR1": ("now", "Run now"), "IR3": ("now", "Run now"), "IRV1": ("now", "Run now"),
    "IR2": ("twin", "Hold · needs clinical sign-off"),
}

SHOW_ID = {"MV1": "MV1-T", "LV1": "LV1-T", "LV2": "LV2-T", "LV3": "LV3-T", "MC": "MC1–5", "LC": "LC1–5"}
RATIOS = [("9x16", "9:16 · Stories + Reels"), ("4x5", "4:5 · Feed")]


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


def iron_copy():
    doc = open(os.path.join(STUDIO, "static/COPY-IRON.md")).read()
    return {m[1]: dict(title=m[2], primary=m[3].strip(), headline=m[4], description=m[5].strip())
            for m in re.finditer(r'### (IRV?\d) · "(.*?)"[^\n]*\n\*\*Primary text:\*\* (.*?)\n\*\*Headline:\*\* (.*?) · \*\*Description:\*\* (.*?)\n', doc)}


# ------------------------------------------------------------------ html pieces
def copy_field(label, text, rows=None):
    t = esc(text)
    body = f'<textarea readonly rows="{rows}">{t}</textarea>' if rows else f'<div class="val">{t}</div>'
    return (f'<div class="field"><div class="flabel">{esc(label)}<button class="copy" data-copy="{t}">Copy</button></div>'
            f'{body}</div>')


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


def build():
    for d in ("previews-web", "files", "static-ads"):   # rebuilt every run
        shutil.rmtree(os.path.join(HERE, d), ignore_errors=True)
    vc = video_copy()
    r1, r2, car, r3 = static_copy()
    zips = {"videos": [], "r1": [], "r2": [], "r3": [], "r4": []}
    ir = iron_copy()
    counts = dict(video=0, static=0, reels=0)

    # ---------------- video ads
    vids_html = []
    for vid, svc, folder, name, line in VIDEOS:
        out = os.path.join(STUDIO, "out", folder)
        c = vc[vid]
        cuts_html = []
        for k, cut in CUTS:
            files, d = [], None
            for r, rlabel in RATIOS:
                src = os.path.join(out, f"{name}_{cut}_{r}.mp4")
                d = d or dur(src)
                asset = f"{vid}-{k}_{cut}_{r}.mp4"
                files.append(dl(stage(src, asset), rlabel, mb(src), primary=(r == "9x16")))
                zips["videos"].append((src, f"Meta ads/{vid} {cut}/{asset}"))
                th = os.path.join(out, f"{name}_{cut}_{r}_thumb.jpg")
                files.append(dl(put(th, f"files/{vid}-{k}_thumbnail_{r}.jpg"), f"Thumbnail {r.replace('x', ':')}", mb(th)))
                zips["videos"].append((th, f"Meta ads/{vid} {cut}/{vid}-{k}_thumbnail_{r}.jpg"))
                counts["video"] += 1
            srt = os.path.join(out, f"{name}_{cut}.srt")
            files.append(dl(put(srt, f"files/{vid}-{k}_captions.srt"), "Captions .srt (optional)", mb(srt)))
            poster = f"previews/{name}_{cut}_9x16.jpg"
            cuts_html.append(f'''
        <div class="cut">
          <video src="previews/{name}_{cut}_9x16.mp4" poster="{poster}" controls playsinline preload="none"></video>
          <div class="cutmeta"><span class="tag">{vid}-{k}</span><b>{cut} · {d}</b></div>
          <div class="dls">{"".join(files)}</div>
        </div>''')
        alt = copy_field("Alt headline", c["alt"]) if c.get("alt") else ""
        vids_html.append(f'''
    <article class="card ad" id="{vid}">
      <header class="adhead"><span class="svc {svc}">{SERVICES[svc]["name"]}</span> {badge(vid)}<h3><span class="id">{vid}</span> {esc(line)}</h3>
        <p class="note">Ad name <code>{vid}-T</code>. Upload the 4:5 and 9:16 files as one ad.</p></header>
      <div class="adbody">
        <div class="cuts one">{"".join(cuts_html)}</div>
        <div class="copyblock">
          {copy_field("Primary text (short)", c["short"], 3)}
          {copy_field("Primary text (long)", c["long"], 8)}
          {copy_field("Headline", c["headline"])}{alt}
          {copy_field("Description", c["description"])}
          {copy_field("Website URL", SERVICES[svc]["dest"])}
          {copy_field("URL parameters", SERVICES[svc]["utm"])}
          <div class="field"><div class="flabel">Call to action</div><div class="val">Book now</div></div>
        </div>
      </div>
    </article>''')

    # ---------------- instagram reels
    reels_html = []
    for vid, svc, folder, name, line in VIDEOS:
        out = os.path.join(STUDIO, "out", folder)
        src = os.path.join(out, f"{name}_IG_Tight_9x16.mp4")
        if not os.path.exists(src):
            continue
        counts["reels"] += 1
        cov = os.path.join(out, f"{name}_IG_cover_9x16.jpg")
        reel_url = stage(src, f"IG-REEL_{vid}.mp4")
        cov_rel = put(cov, f"files/IG-REEL_{vid}_cover.jpg")
        zips["videos"] += [(src, f"Instagram reels/IG-REEL_{vid}.mp4"), (cov, f"Instagram reels/IG-REEL_{vid}_cover.jpg")]
        kw = "LONGEVITY" if svc == "longevity" else "MENOPAUSE"
        reels_html.append(f'''
      <article class="card reel">
        <div class="reelmedia">
          <video src="previews/{name}_IG_Tight_9x16.mp4" poster="{cov_rel}" controls playsinline preload="none"></video>
          <img src="{cov_rel}" alt="{vid} Instagram cover" loading="lazy">
        </div>
        <div class="reelmeta">
          <h3><span class="id">{vid}</span> {esc(line)}</h3>
          <p class="note">{dur(src)} · ends on “Comment {kw}”, which triggers the auto-DM.</p>
          <div class="dls">{dl(reel_url, "Reel .mp4", mb(src), True)}{dl(cov_rel, "Cover .jpg", mb(cov))}</div>
          {copy_field("Caption", vc[vid]["caption"], 9)}
        </div>
      </article>''')

    # ---------------- static ads
    def static_card(ad, title, primary, headline, description, imgs, round_key, alt_note=""):
        files = []
        for label, src in imgs:
            rel = put(src, f"static-ads/{round_key}/{os.path.basename(src)}")
            files.append(dl(rel, label, mb(src), primary=label.startswith("4:5")))
            zips[round_key].append((src, os.path.basename(src)))
            counts["static"] += 1
        th = thumb(imgs[0][1], f"static-ads/{round_key}/thumbs/{ad}.jpg")
        desc = copy_field("Description", description) if description else ""
        return f'''
      <article class="card static" id="{ad}">
        <img src="{th}" alt="{esc(ad)}" loading="lazy">
        <div class="smeta">{badge(ad)}<h4><span class="id">{ad}</span> {esc(title)}</h4>
          <div class="dls">{"".join(files)}</div>
          {copy_field("Primary text", primary, 4)}{copy_field("Headline", headline)}{desc}{alt_note}</div>
      </article>'''

    sdir = os.path.join(STUDIO, "static/out")
    r1_html = {"menopause": [], "longevity": []}
    for ad, c in r1.items():
        sub = "meno" if ad[0] == "M" else "long"
        imgs = [("4:5 Feed", os.path.join(sdir, sub, f"{ad}_4x5.png")), ("9:16 Stories+Reels", os.path.join(sdir, sub, f"{ad}_9x16.png"))]
        r1_html["menopause" if ad[0] == "M" else "longevity"].append(
            static_card(ad, c["title"], c["primary"], c["headline"], c["description"], imgs, "r1"))
    r2_html = {"menopause": [], "longevity": []}
    for ad, c in r2.items():
        sub = "meno" if ad[0] == "M" else "long"
        imgs = [("4:5 Feed", os.path.join(sdir, "r2", sub, f"{ad}_4x5.png")), ("9:16 Stories+Reels", os.path.join(sdir, "r2", sub, f"{ad}_9x16.png"))]
        r2_html["menopause" if ad[0] == "M" else "longevity"].append(
            static_card(ad, c["title"], c["primary"], c["headline"], None, imgs, "r2"))
    r3_html = {"menopause": [], "longevity": []}
    for ad, c in r3.items():
        sub = "meno" if ad[0] == "M" else "long"
        imgs = [("4:5 Feed", os.path.join(sdir, "r3", sub, f"{ad}_4x5.png")), ("9:16 Stories+Reels", os.path.join(sdir, "r3", sub, f"{ad}_9x16.png"))]
        r3_html["menopause" if ad[0] == "M" else "longevity"].append(
            static_card(ad, c["title"], c["primary"], c["headline"], c["description"], imgs, "r3"))
    car_html = []
    for key, svc in (("MC", "menopause"), ("LC", "longevity")):
        sub = "meno-carousel" if key == "MC" else "long-carousel"
        cards = []
        for i, (cid, onimg, chead) in enumerate(car[key]["cards"], 1):
            src = os.path.join(sdir, "r2", sub, f"{cid}_card{i}.png")
            rel = put(src, f"static-ads/r2/{os.path.basename(src)}")
            zips["r2"].append((src, f"{key} carousel/{os.path.basename(src)}"))
            th = thumb(src, f"static-ads/r2/thumbs/{cid}.jpg", 360)
            counts["static"] += 1
            cards.append(f'<figure><img src="{th}" alt="{cid}" loading="lazy"><figcaption><b>{cid}</b> {copy_field("Card headline", chead)}'
                         f'{dl(rel, "Card .png", mb(src), True)}</figcaption></figure>')
        car_html.append(f'''
      <article class="card carousel" id="{key}">{badge(key)}<h4><span class="id">{key}1–{key}5</span> {SERVICES[svc]["name"]} carousel · 5 cards, 4:5</h4>
        <div class="cards">{"".join(cards)}</div>{copy_field("Primary text", car[key]["primary"], 2)}</article>''')

    # ---------------- IV iron (round 4): three statics + the one AI video, files small enough to live in the repo
    idir = os.path.join(sdir, "r4", "iron")
    iron_html = []
    for ad in ("IR1", "IR3", "IR2"):   # run-now first, the held one last
        c = ir[ad]
        imgs = [("4:5 Feed", os.path.join(idir, f"{ad}_4x5.png")), ("9:16 Stories+Reels", os.path.join(idir, f"{ad}_9x16.png"))]
        iron_html.append(static_card(ad, c["title"], c["primary"], c["headline"], c["description"], imgs, "r4"))
    c = ir["IRV1"]
    files = []
    for r, rlabel in RATIOS:
        src = os.path.join(idir, f"IRV1_{r}.mp4"); th = os.path.join(idir, f"IRV1_{r}_thumb.jpg")
        files.append(dl(put(src, f"static-ads/r4/IRV1_{r}.mp4"), rlabel, mb(src), primary=(r == "9x16")))
        files.append(dl(put(th, f"static-ads/r4/IRV1_thumbnail_{r}.jpg"), f"Thumbnail {r.replace('x', ':')}", mb(th)))
        zips["r4"] += [(src, f"IRV1_{r}.mp4"), (th, f"IRV1_thumbnail_{r}.jpg")]
    iron_video = f'''
    <article class="card ad" id="IRV1">
      <header class="adhead"><span class="svc iron">IV iron</span> {badge("IRV1")}<h3><span class="id">IRV1</span> {esc(c["title"])}</h3>
        <p class="note">The one AI video: a 6-second push-in on the empty infusion room, then the waitlist end card. Ad name <code>IRV1</code>. Upload the 4:5 and 9:16 files as one ad.</p></header>
      <div class="adbody">
        <div class="cuts one"><div class="cut">
          <video src="static-ads/r4/IRV1_9x16.mp4" poster="static-ads/r4/IRV1_thumbnail_9x16.jpg" controls playsinline preload="none"></video>
          <div class="cutmeta"><span class="tag">IRV1</span><b>0:06 · quiet music bed</b></div>
          <div class="dls">{"".join(files)}</div></div></div>
        <div class="copyblock">
          {copy_field("Primary text", c["primary"], 5)}{copy_field("Headline", c["headline"])}{copy_field("Description", c["description"])}
          <div class="field"><div class="flabel">Call to action</div><div class="val">Sign up</div></div>
        </div>
      </div>
    </article>'''

    # ---------------- zips (release assets)
    # Static rounds get a zip each. Videos don't: a video zip would re-upload ~600 MB of files that are
    # already individual release assets, so "all video files" links to the release page instead.
    for key, fname, extra in (("r1", f"Optimal-static-ads-round-1_{TAG}.zip", [(os.path.join(STUDIO, "static/COPY.md"), "COPY.md")]),
                              ("r2", f"Optimal-static-ads-round-2_{TAG}.zip", [(os.path.join(STUDIO, "static/COPY-R2.md"), "COPY.md")]),
                              ("r3", f"Optimal-static-ads-round-3_{TAG}.zip", [(os.path.join(STUDIO, "static/COPY-R3.md"), "COPY.md")]),
                              ("r4", f"Optimal-IV-iron-ads_{TAG}.zip", [(os.path.join(STUDIO, "static/COPY-IRON.md"), "COPY.md")])):
        if not os.path.exists(os.path.join(STAGE, fname)):
            with zipfile.ZipFile(os.path.join(STAGE, fname), "w", zipfile.ZIP_STORED) as z:
                for src, arc in zips[key] + extra:
                    z.write(src, arc)
    vid_total = sum(os.path.getsize(src) for src, arc in zips["videos"])
    zsize = {"videos": f"{len([a for _, a in zips['videos'] if a.endswith('.mp4')])} files · {vid_total / 1e6:.0f} MB",
             "r1": mb(os.path.join(STAGE, f"Optimal-static-ads-round-1_{TAG}.zip")),
             "r2": mb(os.path.join(STAGE, f"Optimal-static-ads-round-2_{TAG}.zip")),
             "r3": mb(os.path.join(STAGE, f"Optimal-static-ads-round-3_{TAG}.zip")),
             "r4": mb(os.path.join(STAGE, f"Optimal-IV-iron-ads_{TAG}.zip"))}
    shutil.copy2(os.path.join(STUDIO, "brand/ds/assets/logos/OptimalLogo-Green.png"), os.path.join(HERE, "files", "logo.png"))

    thumbs, titles = {}, {}
    for vid, svc, folder, name, line in VIDEOS:
        thumbs[vid], titles[vid] = f"previews/{name}_Tight_9x16.jpg", line
    for ad, c in r1.items():
        thumbs[ad], titles[ad] = f"static-ads/r1/thumbs/{ad}.jpg", c["title"]
    for ad, c in r2.items():
        thumbs[ad], titles[ad] = f"static-ads/r2/thumbs/{ad}.jpg", c["title"]
    for ad, c in r3.items():
        thumbs[ad], titles[ad] = f"static-ads/r3/thumbs/{ad}.jpg", c["title"]
    for key in ("MC", "LC"):
        thumbs[key] = f"static-ads/r2/thumbs/{key}1.jpg"
        titles[key] = "Menopause carousel, 5 cards" if key == "MC" else "Longevity carousel, 5 cards"
    for k, *_ in REWRITES:   # carousel cards (MC1, LC5…) use their own thumbnails
        thumbs.setdefault(k, f"static-ads/r2/thumbs/{k}.jpg")
    missing = [k for k in PLAN if not os.path.exists(os.path.join(HERE, thumbs.get(k, "-")))]
    assert not missing, f"plan thumbnails missing: {missing}"

    page = TEMPLATE
    for k, v in {
        "ROUND": ROUND, "TAG": TAG,
        "ZIP_VIDEOS": f"https://github.com/{REPO}/releases/tag/{TAG}", "ZIP_R1": REL + f"Optimal-static-ads-round-1_{TAG}.zip",
        "ZIP_R2": REL + f"Optimal-static-ads-round-2_{TAG}.zip", "ZIP_R3": REL + f"Optimal-static-ads-round-3_{TAG}.zip", "ZS_R3": zsize["r3"],
        "ZS_VIDEOS": zsize["videos"], "ZS_R1": zsize["r1"], "ZS_R2": zsize["r2"],
        "N_VIDEO": str(len(VIDEOS)), "N_STATIC": str(len(r1) + len(r2) + len(r3)), "N_CAR": "2", "N_REELS": str(counts["reels"]),
        "VIDEO_ADS": "".join(vids_html), "REELS": "".join(reels_html),
        "R1_MENO": "".join(r1_html["menopause"]), "R1_LONG": "".join(r1_html["longevity"]),
        "R2_MENO": "".join(r2_html["menopause"]), "R2_LONG": "".join(r2_html["longevity"]), "CAROUSELS": "".join(car_html),
        "R3_MENO": "".join(r3_html["menopause"]), "R3_LONG": "".join(r3_html["longevity"]),
        "IRON_STATICS": "".join(iron_html), "IRON_VIDEO": iron_video,
        "ZIP_R4": REL + f"Optimal-IV-iron-ads_{TAG}.zip", "ZS_R4": zsize["r4"],
        "PLAN": plan_html(thumbs, titles), "REWRITES": rewrites_html(thumbs), "N_TEST": str(sum(1 for v in PLAN.values() if v[0] == "now")),
        "N_ALL": str(len(PLAN)),
        "M_DEST": SERVICES["menopause"]["dest"], "L_DEST": SERVICES["longevity"]["dest"],
        "M_UTM": esc(SERVICES["menopause"]["utm"]), "L_UTM": esc(SERVICES["longevity"]["utm"]),
    }.items():
        page = page.replace("{{" + k + "}}", v)
    open(os.path.join(HERE, "index.html"), "w").write(page)
    print(f"built: {len(VIDEOS)} video ads, {counts['reels']} reels, {len(r1) + len(r2)} static singles + 2 carousels; "
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
        run("git", "commit", "-q", "-m", f"Hand-off site: {ROUND} ads\n\nCo-Authored-By: Claude <noreply@anthropic.com>")
    run("git", "push", "-q", "origin", "main")


TEMPLATE = open(os.path.join(HERE, "template.html")).read()

if __name__ == "__main__":
    build()
    if "--publish" in sys.argv:
        publish()
