"""Fetch WIPO Lex details pages for Ghana and list their text/PDF links. 1 request/s."""
import os
import re, html, sys, time, urllib.request, json
from pathlib import Path
UA = {"User-Agent": "Mozilla/5.0 (compatible; LexifinaLawArchive/1.0; +https://lexifina.com)"}
C = Path(os.path.join(os.environ.get("GH_ACQ", "."), 'sec/cache/wipo'))
C.mkdir(parents=True, exist_ok=True)
out = {}
for i in sys.argv[1:]:
    f = C / f"details-{i}.html"
    if not f.exists():
        f.write_bytes(urllib.request.urlopen(urllib.request.Request(
            f"https://www.wipo.int/wipolex/en/legislation/details/{i}", headers=UA), timeout=60).read())
        time.sleep(1)
    t = f.read_text("utf8")
    links = sorted(set(re.findall(r'href="([^"]*(?:/edocs/lexdocs/[^"]+|/wipolex/en/text/\d+|\.pdf)[^"]*)"', t)))
    dates = re.findall(r"(Entry into force|Adopted|Enacted|Promulgated|Issued|Date of Text)[^<]*</[^>]+>\s*<[^>]+>\s*([^<]{4,40})", t)
    title = re.search(r"<title>(.*?)</title>", t, re.S).group(1).strip()
    out[i] = dict(title=html.unescape(title), links=links)
    print(i, html.unescape(title)[:100])
    for l in links:
        print("    ", l)
    for m in re.finditer(r"(Entry into force|Adopted|Enacted|Promulgated|Issued|Date)\s*:?\s*</[^>]+>(.{0,200})", t, re.S):
        print("     D", m.group(1), re.sub(r"<[^>]+>|\s+", " ", m.group(2)).strip()[:80])
(C / "details.json").write_text(json.dumps(out, indent=1), "utf8")
