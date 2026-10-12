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
ROUND = "October 12, 2026"
REL = f"https://github.com/{REPO}/releases/download/{TAG}/"
STAGE = os.path.join(HERE, "release")          # git-ignored: what gets uploaded to the release

SERVICES = {
    "longevity": dict(name="Longevity membership", dest="https://www.beoptimal.ca/membership",
                      utm="utm_source=meta&utm_medium=paid&utm_campaign=opt-b-q4&utm_content={{ad.name}}"),
    "menopause": dict(name="Menopause", dest="https://www.beoptimal.ca/services/menopause-and-perimenopause-care",
                      utm="utm_source=meta&utm_medium=paid&utm_campaign=opt-a-q4&utm_content={{ad.name}}"),
}
VIDEOS = [  # id, service, folder in meta-ad-studio/out, render name, the line on screen
    ("LV1", "longevity", "longevity-core-v2", "LongevityCore", "3 things to know before you book."),
    ("LV2", "longevity", "longevity-ad2", "LongevityFullHour", "A full hour. Every year."),
    ("MV1", "menopause", "menopause-ad1", "MenopauseMyself", "“I just don’t feel like myself.”"),
]
CUTS = [("T", "Tight"), ("F", "Full")]
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
    if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src):
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
    return one, two, car


# ------------------------------------------------------------------ html pieces
def copy_field(label, text, rows=None):
    t = esc(text)
    body = f'<textarea readonly rows="{rows}">{t}</textarea>' if rows else f'<div class="val">{t}</div>'
    return (f'<div class="field"><div class="flabel">{esc(label)}<button class="copy" data-copy="{t}">Copy</button></div>'
            f'{body}</div>')


def dl(href, label, size, primary=False):
    return (f'<a class="dl{" primary" if primary else ""}" href="{esc(href)}" download>'
            f'<span>{esc(label)}</span><em>{esc(size)}</em></a>')


def build():
    for d in ("previews-web", "files", "static-ads"):
        shutil.rmtree(os.path.join(HERE, d), ignore_errors=True)
    vc = video_copy()
    r1, r2, car = static_copy()
    zips = {"videos": [], "r1": [], "r2": []}
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
      <header class="adhead"><span class="svc {svc}">{SERVICES[svc]["name"]}</span><h3><span class="id">{vid}</span> {esc(line)}</h3>
        <p class="note">Ad names <code>{vid}-T</code> and <code>{vid}-F</code>. Upload the 4:5 and 9:16 files as one ad.</p></header>
      <div class="adbody">
        <div class="cuts">{"".join(cuts_html)}</div>
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
        <div class="smeta"><h4><span class="id">{ad}</span> {esc(title)}</h4>
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
      <article class="card carousel"><h4><span class="id">{key}1–{key}5</span> {SERVICES[svc]["name"]} carousel · 5 cards, 4:5</h4>
        <div class="cards">{"".join(cards)}</div>{copy_field("Primary text", car[key]["primary"], 2)}</article>''')

    # ---------------- zips (release assets)
    # Static rounds get a zip each. Videos don't: a video zip would re-upload ~600 MB of files that are
    # already individual release assets, so "all video files" links to the release page instead.
    for key, fname, extra in (("r1", f"Optimal-static-ads-round-1_{TAG}.zip", [(os.path.join(STUDIO, "static/COPY.md"), "COPY.md")]),
                              ("r2", f"Optimal-static-ads-round-2_{TAG}.zip", [(os.path.join(STUDIO, "static/COPY-R2.md"), "COPY.md")])):
        if not os.path.exists(os.path.join(STAGE, fname)):
            with zipfile.ZipFile(os.path.join(STAGE, fname), "w", zipfile.ZIP_STORED) as z:
                for src, arc in zips[key] + extra:
                    z.write(src, arc)
    vid_total = sum(os.path.getsize(src) for src, arc in zips["videos"])
    zsize = {"videos": f"{len([a for _, a in zips['videos'] if a.endswith('.mp4')])} files · {vid_total / 1e6:.0f} MB",
             "r1": mb(os.path.join(STAGE, f"Optimal-static-ads-round-1_{TAG}.zip")),
             "r2": mb(os.path.join(STAGE, f"Optimal-static-ads-round-2_{TAG}.zip"))}
    shutil.copy2(os.path.join(STUDIO, "brand/ds/assets/logos/OptimalLogo-Green.png"), os.path.join(HERE, "files", "logo.png"))

    page = TEMPLATE
    for k, v in {
        "ROUND": ROUND, "TAG": TAG,
        "ZIP_VIDEOS": f"https://github.com/{REPO}/releases/tag/{TAG}", "ZIP_R1": REL + f"Optimal-static-ads-round-1_{TAG}.zip",
        "ZIP_R2": REL + f"Optimal-static-ads-round-2_{TAG}.zip",
        "ZS_VIDEOS": zsize["videos"], "ZS_R1": zsize["r1"], "ZS_R2": zsize["r2"],
        "N_VIDEO": str(len(VIDEOS)), "N_STATIC": str(len(r1) + len(r2)), "N_CAR": "2", "N_REELS": str(counts["reels"]),
        "VIDEO_ADS": "".join(vids_html), "REELS": "".join(reels_html),
        "R1_MENO": "".join(r1_html["menopause"]), "R1_LONG": "".join(r1_html["longevity"]),
        "R2_MENO": "".join(r2_html["menopause"]), "R2_LONG": "".join(r2_html["longevity"]), "CAROUSELS": "".join(car_html),
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
