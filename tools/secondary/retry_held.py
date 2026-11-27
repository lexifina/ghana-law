"""Retry held Library Acts (reader-type reasons) with the Assembly Press reader (marg_read) and wipo_read."""
import os
import json, sys
from pathlib import Path
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "sec"))
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "tools"))
import build as B, marg_read as M, wipo_read as W
ROOT = Path(os.environ.get("GH_ACQ", "."))
nums = [int(x) for x in sys.argv[1].split(",")]
cat = B.catalogue()
out = {}
for n in nums:
    for c in cat.get(n, []):
        for s in c["pdfs"]:
            f = ROOT / "cache/pdf" / f"{s['uuid']}.pdf"
            if not f.exists():
                print(n, "missing", s["uuid"]); continue
            for name, fn in (("build", lambda: B.read(f.read_bytes())), ("marg", lambda: M.read(str(f), "act")),
                             ("wipo", lambda: W.read(str(f)))):
                try:
                    u, e, meta = fn()
                except Exception as ex:
                    u, e, meta = None, f"EXC {ex}", {}
                print(n, c["revised"], name, "OK" if u else "--", len(u or {}), meta.get("assent"), meta.get("gazette"),
                      meta.get("commencement"), meta.get("sections"), (e or "")[:80], "|", c["name"][:60], s["uuid"][:8])
