"""Download the WIPO Lex PDF linked from each cached details page; report text-layer density."""
import os
import re, html, sys, time, urllib.request, json, hashlib
from pathlib import Path
UA = {"User-Agent": "Mozilla/5.0 (compatible; LexifinaLawArchive/1.0; +https://lexifina.com)"}
C = Path(os.path.join(os.environ.get("GH_ACQ", "."), 'sec/cache/wipo'))
for i in sys.argv[1:]:
    t = (C / f"details-{i}.html").read_text("utf8")
    links = [html.unescape(l) for l in re.findall(r'href="(https://wipolex-res\.wipo\.int/edocs/lexdocs/[^"]+)"', t)]
    for l in sorted(set(links)):
        name = re.search(r"/([^/?]+)\?", l).group(1)
        f = C / name
        if not f.exists():
            f.write_bytes(urllib.request.urlopen(urllib.request.Request(l, headers=UA), timeout=120).read())
            time.sleep(1)
        b = f.read_bytes()
        if name.endswith(".pdf"):
            import pymupdf
            d = pymupdf.open(f)
            txt = "".join(p.get_text() for p in d)
            print(i, name, d.page_count, "pages", len(txt) // max(1, d.page_count), "chars/page", hashlib.sha256(b).hexdigest()[:12],
                  d.metadata.get("producer"), d.metadata.get("creator"))
        else:
            print(i, name, len(b))
