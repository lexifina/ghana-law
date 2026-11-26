"""Test every fetched FAOLEX PDF for Ghana: Act number (from the ECOLEX title), already in repo?, readers' verdicts."""
import os
import json, re, sys, os
from pathlib import Path
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "sec"))
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "tools"))
import marg_read as M, wipo_read as W, build as B
import pymupdf
C = Path(os.path.join(os.environ.get("GH_ACQ", "."), 'sec/cache'))
REPO = Path(os.path.join(os.environ.get("GH_ACQ", "."), 'repo'))
have = {int(re.match(r"(\d+)-", p.name).group(1)) for p in REPO.glob("acts/*/*") if re.match(r"\d+-", p.name)}
recs = json.load(open(C / "ecolex/list.json", encoding="utf8"))
out = []
for i, r in recs.items():
    t = r["title"]
    if re.search(r"\b(L\.?\s?I\.?|C\.?\s?I\.?|E\.?\s?I\.?)\s*\d+|Regulations|Rules|Policy|Plan|Strategy|Programme|Guidelines|Framework|Order|Notice|Bye-?laws?", t, re.I):
        continue
    m = re.search(r"\((?:Act|No\.?)\s*(\d{1,4})\)|Act\s*(\d{3,4})\b", t)
    num = int(m.group(1) or m.group(2)) if m else None
    f = C / "faolex" / f"gha{i}.pdf"
    if not f.exists():
        continue
    if num and num in have:
        continue
    try:
        d = pymupdf.open(f)
        txt = "\n".join(p.get_text() for p in d)
        dens = len(txt) // max(1, d.page_count)
        prod = d.metadata.get("producer") or ""
    except Exception as e:
        print("ERR", i, t, e)
        continue
    res = {}
    for name, fn in (("wipo", lambda: W.read(str(f))), ("marg", lambda: M.read(str(f), "act"))):
        try:
            u, e, meta = fn()
        except Exception as ex:
            u, e, meta = None, f"EXC {ex}"[:60], {}
        res[name] = (bool(u), (e or "")[:70], meta.get("assent"), meta.get("gazette"), meta.get("sections"))
    ok = [k for k, v in res.items() if v[0]]
    out.append(dict(id=i, title=t, num=num, dens=dens, producer=prod, ok=ok, res=res))
    print("OK " if ok else "-- ", i, num, dens, prod[:20], "|", t[:70], "|", ok or res["marg"][1][:60])
json.dump(out, open(C.parent / "faolex_scan.json", "w", encoding="utf8"), indent=1)
