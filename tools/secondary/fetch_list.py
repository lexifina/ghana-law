"""Fetch the given URLs into sec/cache/gov/<host>/ (1.2 s apart), then print reader verdicts and Act numbers."""
import os
import collections, re, sys, time, urllib.parse, urllib.request
from pathlib import Path
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "sec"))
import marg_read as M, wipo_read as W
import pymupdf
UA = {"User-Agent": "Mozilla/5.0 (compatible; LexifinaLawArchive/1.0; +https://lexifina.com)"}
C = Path(os.path.join(os.environ.get("GH_ACQ", "."), 'sec/cache/gov'))
for u in sys.argv[1:]:
    h = urllib.parse.urlparse(u).netloc.removeprefix("www.")
    f = C / h / urllib.parse.unquote(u.rsplit("/", 1)[1])
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        try:
            f.write_bytes(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=120).read())
        except Exception as e:
            print("ERR", u, e); continue
        time.sleep(1.2)
    try:
        d = pymupdf.open(f)
        t = "\n".join(p.get_text() for p in d)
    except Exception as e:
        print("BAD", f, e); continue
    c = collections.Counter(re.findall(r"^\s*A[Cc][Tt]\s+(\d{3,4})\s*$", t, re.M)).most_common(1)
    print("==", f, d.page_count, "pp", len(t) // max(1, d.page_count), "c/pp; Act", c)
    for name, fn in (("marg", lambda: M.read(str(f), "act")), ("wipo", lambda: W.read(str(f)))):
        try:
            un, e, m = fn()
        except Exception as ex:
            un, e, m = None, f"EXC {ex}", {}
        print("  ", "OK " if un else "-- ", name, len(un or {}), m.get("assent"), m.get("gazette"), m.get("sections"),
              (e or "")[:80])
