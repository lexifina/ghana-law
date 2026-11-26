"""Run marg_read over Library items not yet in the repo (held for heading format, or skipped by build.catalogue)."""
import os
import json, os, re, sys
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "sec"))
import marg_read as M
ROOT = os.environ.get("GH_ACQ", ".")
held = json.load(open(ROOT + "/held.json", encoding="utf8"))
held_nums = {k for k, v in held.items() if "Section N" in v["why"] or "sections" in v["why"] or "word check" in v["why"]}
out = []
for l in open(ROOT + "/catalogue.jsonl", encoding="utf8"):
    r = json.loads(l)
    n = re.sub(r"\s+", " ", r["name"]).strip()
    if re.search(r"\bBill\b|Report of|Memorandum|Instructions for|Revis|Reviwed|Deportation|Prohibition of Entry", n, re.I):
        continue
    m = re.search(r"\bACT\s*\.?\s*(\d{1,4})\b", n, re.I)
    import build as B
    am = B.ACT_RE.search(n)
    if am and str(int(am.group("num"))) not in held_nums:
        continue
    kind = "instrument" if re.search(r"Instrument|Regulations|Rules|Order|\b[CLE]\.\s?I\b|\bL1\b", n) else "act"
    for b in r["bitstreams"]:
        f = f"{ROOT}/cache/pdf/{b['uuid']}.pdf"
        if b["bundle"] != "ORIGINAL" or not os.path.exists(f):
            continue
        try:
            u, e, meta = M.read(f, kind)
        except Exception as ex:
            u, e, meta = None, f"EXC {type(ex).__name__} {ex}"[:90], {}
        meta.pop("dropped", None)
        out.append(dict(name=n, handle=r["handle"], uuid=b["uuid"], url=b.get("url"), kind=kind, ok=bool(u), err=e,
                        n=len(u or {}), **{k: meta.get(k) for k in ("assent", "gazette", "made", "sections", "pages")}))
        x = out[-1]
        print("OK " if x["ok"] else "-- ", kind[:4], x["n"], x["assent"], x["gazette"], x["made"], n[:70], "" if x["ok"] else (e or "")[:70])
        if u:
            break
json.dump(out, open(ROOT + "/sec/scan_marg.json", "w", encoding="utf8"), indent=1)
print(sum(x["ok"] for x in out), "ok of", len(out))
