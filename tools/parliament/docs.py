"""Refresh the counts in README.md, data/laws.csv and data/paths.json for Acts added by tools/parliament/build.py,
then commit (documentation) if anything changed.   python -X utf8 tools/docs.py <repo>"""
import csv, io, json, os, re, subprocess, sys
from pathlib import Path

repo = Path(sys.argv[1])


def git(*a):
    return subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, encoding="utf8").stdout


log = git("log", "--format=%H%x00%at%x00%B%x01")
added, revised, pre1970 = [], [], 0
for rec in log.split("\x01"):
    if not rec.strip():
        continue
    h, at, body = rec.strip("\n").split("\x00", 2)
    if int(at) < 86400:
        pre1970 += 1
    tr = dict(re.findall(r"^([A-Za-z-]+): (.*)$", body, re.M))
    if tr.get("Text-source") == "publisher text layer":
        added.append(tr)
    elif tr.get("Text-source") == "publisher text layer (Revised Edition)":
        tr["Law"] = tr["Law"].replace(" (Revised Edition)", "")
        revised.append(tr)
k, rv = len(added), len(revised)
rows = list(csv.DictReader(open(repo / "data/laws.csv", encoding="utf8")))
fields = list(rows[0].keys())
have = {r["key"] for r in rows}
pj = json.loads((repo / "data/paths.json").read_text("utf8"))
folders = {}
for d in repo.glob("acts/*/*"):
    m = re.match(r"(\d+)-", d.name)
    if m:
        folders[int(m.group(1))] = f"acts/{d.parent.name}/{d.name}"
for tr in added + revised:
    num = int(tr["Law"].split()[-1])
    key = f"act-{num}"
    folder = folders.get(num)
    if folder:
        pj["paths"].setdefault(f"act-{num:04d}", folder)
    if key in have:
        continue
    title = open(repo / folder / "README.md", encoding="utf8").readline()[2:].strip() if folder else tr.get("Act", "")
    have.add(key)
    rows.append({"key": key, "label": tr["Law"], "kind": "law" if tr in added else "consolidation", "title": title,
                 "enacted": tr.get("Enacted", ""),
                 "published": tr.get("Published", ""), "in_force_days": tr["In-force"], "commits": "1",
                 "url": tr["Source"]})
buf = io.StringIO()
w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
w.writeheader()
w.writerows(rows)
(repo / "data/laws.csv").write_bytes(buf.getvalue().encode("utf8"))
(repo / "data/paths.json").write_bytes((json.dumps(pj, indent=0, ensure_ascii=False) + "\n").encode("utf8"))
n_acts = 149 + k + rv
years = [int(r["in_force_days"][:4]) for r in rows if r["in_force_days"][:4].isdigit()]
readme = (repo / "README.md").read_text("utf8")
readme = re.sub(r"\*\*What is in it now:\*\* \d+ Acts of Parliament from 1960 to \d{4}, with \d+ versions: \d+ from the "
                r"Parliament of Ghana Library's repository, \d+ of them as passed",
                f"**What is in it now:** {n_acts} Acts of Parliament from 1960 to {max(years)}, with {150 + k + rv} versions: "
                f"{145 + k + rv} from the Parliament of Ghana Library's repository, {143 + k} of them as passed", readme)
readme = re.sub(r"so the \d+ commits for Acts of 1960 to 1965", f"so the {pre1970} commits for Acts of 1960 to 1969",
                readme)
readme = re.sub(r"\| \d+ Acts; the PDFs' text layer \|", f"| {145 + k + rv} Acts; the PDFs' text layer |", readme)
readme = re.sub(r"and 2 \(the Electronic Transactions Act, 2008 and the Corporate Insolvency and Restructuring Act, 2020\) in "
                r"the Library's consolidated edition(?: and \d+ Revised Editions \(consolidations dated by the latest law "
                r"they include\))?",
                f"and 2 (the Electronic Transactions Act, 2008 and the Corporate Insolvency and Restructuring Act, 2020) in "
                f"the Library's consolidated edition and {rv} Revised Editions (consolidations dated by the latest law "
                f"they include)", readme)
(repo / "README.md").write_bytes(readme.encode("utf8"))
subprocess.run(["git", "-C", str(repo), "add", "README.md", "data/laws.csv", "data/paths.json"], check=True)
if subprocess.run(["git", "-C", str(repo), "diff", "--cached", "--quiet"]).returncode:
    msg = (f"Documentation: counts and tables for {k} Acts and {rv} Revised Editions added from the Parliament of Ghana Library\n\n"
           f"README counts, data/laws.csv and data/paths.json now include the Acts added on 2026-11-26. No law text "
           f"changes.\n\nIn-force: 2026-11-26\nKind: documentation\n")
    env = dict(os.environ, GIT_AUTHOR_NAME="Lexifina", GIT_AUTHOR_EMAIL="ghana-law@lexifina.com",
               GIT_COMMITTER_NAME="Lexifina", GIT_COMMITTER_EMAIL="ghana-law@lexifina.com",
               GIT_AUTHOR_DATE="2026-11-26T12:00:00+0000", GIT_COMMITTER_DATE="2026-11-26T12:00:00+0000")
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-F", "-"], input=msg.encode(), env=env, check=True)
print(k, "added acts;", rv, "revised;", n_acts, "acts")
