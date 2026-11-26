"""List ECOLEX legislation records for Ghana (listing pages only, 30 s apart per robots Crawl-delay), then fetch the
FAOLEX PDFs (faolex.fao.org, ~1 s apart). Output: sec/cache/ecolex/list.json and sec/cache/faolex/gha<ID>.pdf."""
import os
import json, re, time, html, urllib.request
from pathlib import Path
UA = {"User-Agent": "Mozilla/5.0 (compatible; LexifinaLawArchive/1.0; +https://lexifina.com)"}
C = Path(os.path.join(os.environ.get("GH_ACQ", "."), 'sec/cache'))
(C / "ecolex").mkdir(parents=True, exist_ok=True)
(C / "faolex").mkdir(parents=True, exist_ok=True)
LOG = open(C / "ecolex" / "log.txt", "a", encoding="utf8", buffering=1)


def get(u):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120)
    return r.read()


recs = {}
for page in range(1, 40):
    f = C / "ecolex" / f"page-{page}.html"
    if not f.exists():
        f.write_bytes(get(f"https://www.ecolex.org/result/?type=legislation&xcountry=Ghana&page={page}"))
        time.sleep(30)
    t = f.read_text("utf8")
    items = re.findall(r'<h3 class="search-result-title">\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>(.*?)(?=<h3 class="search-result-title">|</ul>\s*</div>\s*<nav|$)', t, re.S)
    if not items:
        items = [(m.group(1), m.group(2), "") for m in re.finditer(r'href="(/details/legislation/[^"]+)"[^>]*>(.*?)</a>', t, re.S)]
    new = 0
    for href, title, rest in items:
        m = re.search(r"lex-faoc(\d+)", href, re.I)
        if not m or m.group(1) in recs:
            continue
        recs[m.group(1)] = dict(id=m.group(1), href=href, title=html.unescape(re.sub(r"<[^>]+>|\s+", " ", title)).strip(),
                                meta=html.unescape(re.sub(r"<[^>]+>|\s+", " ", rest)).strip()[:300])
        new += 1
    LOG.write(f"page {page}: {new} new, {len(recs)} total\n")
    if new == 0:
        break
(C / "ecolex" / "list.json").write_text(json.dumps(recs, indent=1, ensure_ascii=False), "utf8")
for i in recs:
    f = C / "faolex" / f"gha{i}.pdf"
    if f.exists():
        continue
    try:
        f.write_bytes(get(f"https://faolex.fao.org/docs/pdf/gha{i}.pdf"))
        LOG.write(f"pdf {i} ok\n")
    except Exception as e:
        LOG.write(f"pdf {i} {e}\n")
    time.sleep(1)
LOG.write("done\n")
