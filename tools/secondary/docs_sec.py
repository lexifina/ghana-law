"""Add the laws committed by sec/*.py (after BASE) to data/laws.csv and data/paths.json. Prints counts.
    python -X utf8 sec/docs_sec.py <repo>"""
import csv, io, json, re, subprocess, sys
from pathlib import Path
repo = Path(sys.argv[1])
BASE = "bc890e425d2a1b921a5ce69cda3ac54338ffcb72"
log = subprocess.run(["git", "-C", str(repo), "log", "--reverse", "--format=%H%x00%B%x01", f"{BASE}..HEAD"],
                     capture_output=True, text=True, encoding="utf8").stdout
rows = list(csv.DictReader(open(repo / "data/laws.csv", encoding="utf8")))
fields = list(rows[0].keys())
have = {r["key"] for r in rows}
pj = json.loads((repo / "data/paths.json").read_text("utf8"))
stats = {"law": 0, "instrument": 0, "consolidation": 0, "constitution": 0, "secondary": 0, "ocr": 0}
for rec in log.split("\x01"):
    if not rec.strip():
        continue
    h, body = rec.strip("\n").split("\x00", 1)
    tr = dict(re.findall(r"^([A-Za-z-]+): (.*)$", body, re.M))
    if tr.get("Kind") == "documentation" or "Law" not in tr:
        continue
    files = subprocess.run(["git", "-C", str(repo), "show", "--name-only", "--format=", h], capture_output=True,
                           text=True, encoding="utf8").stdout.split()
    folder = "/".join(files[0].split("/")[:3]) if files[0].startswith(("acts/", "subsidiary/")) else "constitution"
    law = tr["Law"].replace(" (consolidation)", "")
    if folder == "constitution":
        key, kind = ("constitution" if "282" in law else "act-1996-527"), "law"
        title = "Constitution of the Republic of Ghana, 1992" if "282" in law else "Constitution of the Republic of Ghana (Amendment) Act, 1996 (Act 527)"
        stats["constitution"] += 1
    else:
        m = re.match(r"Act (\d+)$", law)
        key = f"act-{m.group(1)}" if m else re.sub(r"[^a-z0-9]+", "-", law.lower()).strip("-")
        kind = tr["Kind"]
        title = open(repo / folder / "README.md", encoding="utf8").readline()[2:].strip()
        stats[kind if kind in stats else "law"] += 1
        pid = f"act-{int(m.group(1)):04d}" if m else key
        pj["paths"].setdefault(pid, folder)
    if "Source-status" in tr:
        stats["secondary"] += 1
    if tr.get("Text-source") == "publisher OCR":
        stats["ocr"] += 1
    if tr["Kind"] == "consolidation":
        key = key + "-consolidated"
    if key in have:
        continue
    have.add(key)
    rows.append({"key": key, "label": law, "kind": "consolidation" if tr["Kind"] == "consolidation" else kind, "title": title,
                 "enacted": tr.get("Enacted", ""), "published": tr.get("Published", ""), "in_force_days": tr["In-force"],
                 "commits": "1", "url": tr.get("Source", "")})
buf = io.StringIO()
w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
w.writeheader()
w.writerows(rows)
(repo / "data/laws.csv").write_bytes(buf.getvalue().encode("utf8"))
(repo / "data/paths.json").write_bytes((json.dumps(pj, indent=0, ensure_ascii=False) + "\n").encode("utf8"))
print(stats, len(rows), "rows")
