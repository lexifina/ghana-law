"""Run build.read (with Regulation/Rule/Paragraph headings allowed) over every catalogue item build.catalogue() skips,
and over every item for numbers the repo lacks. Print ok/err per item. Writes sec/scan_inst.json."""
import os
import json, os, re, sys
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "tools"))
import build as B
B.SEC = re.compile(r"^\s*(?:Section|Regulation|Rule|Paragraph|Order)\s+(\d{1,3}[A-Z]?)\s*[\u2014\u2013\-]+\s*(.*)$")
ROOT = os.environ.get("GH_ACQ", ".")
out = []
for l in open(ROOT + "/catalogue.jsonl", encoding="utf8"):
    r = json.loads(l)
    n = re.sub(r"\s+", " ", r["name"]).strip()
    if re.search(r"\bBill\b|Report of|Memorandum|Instructions for", n, re.I) or B.ACT_RE.search(n):
        continue
    res = None
    for b in r["bitstreams"]:
        f = f"{ROOT}/cache/pdf/{b['uuid']}.pdf"
        if b["bundle"] != "ORIGINAL" or not os.path.exists(f):
            continue
        try:
            units, err, meta = B.read(open(f, "rb").read())
        except Exception as e:
            units, err, meta = None, f"reader error {e}", {}
        res = dict(name=n, handle=r["handle"], uuid=b["uuid"], url=b.get("url"), ok=bool(units), err=err,
                   n=len(units or {}), assent=meta.get("assent"), gazette=meta.get("gazette"),
                   commencement=meta.get("commencement"), issued=(r["md"].get("dc.date.issued") or [""])[0])
        if units:
            break
    if res:
        out.append(res)
        print("OK " if res["ok"] else "-- ", res["n"], res["assent"], res["gazette"], n[:80], "" if res["ok"] else res["err"][:60])
json.dump(out, open(ROOT + "/sec/scan_inst.json", "w", encoding="utf8"), indent=1)
print(sum(x["ok"] for x in out), "ok of", len(out))
