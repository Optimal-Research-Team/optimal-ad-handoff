# Optimal ad hand-off

**Site:** https://optimal-research-team.github.io/optimal-ad-handoff/

One page where the ads team can preview, download and copy everything for an ad round: video ads, static ads, carousels and Instagram reels.

## For the ads team

1. Open the site.
2. Download what you need. Each ad has a **4:5 Feed** file and a **9:16 Stories + Reels** file. To grab everything at once, use the zip buttons at the top.
3. Follow **Launch in six steps** on the page. Every ad card has Copy buttons for its primary text, headline, description, URL and URL parameters.

Full-quality videos and zips download from the GitHub release ([releases](https://github.com/Optimal-Research-Team/optimal-ad-handoff/releases)). The previews on the page are compressed.

## Updating the site (new round or changed ads)

The site is built from the renders in `../meta-ad-studio` (video ads in `out/`, statics in `static/out/`) and their copy (`VIDEO-ADS.md`, `static/COPY.md`, `static/COPY-R2.md`).

```bash
python3 build.py              # rebuild index.html and stage the release files
python3 -m http.server 5420   # optional: check it at http://localhost:5420
python3 build.py --publish    # upload the full-quality files to the release, then commit and push (Pages redeploys in about a minute)
```

To start a new round, change `TAG` and `ROUND` at the top of `build.py`, then add the new ads to `VIDEOS` (statics come from the copy docs).

- **Hosting:** GitHub Pages serves `main` at the repo root. Large files live in the release, never in git (GitHub rejects files over 100 MB).
- **Search engines:** the page is public but marked `noindex`. Everything on it is ad creative that is meant to run publicly.
