"""One pure-rename commit: act/<year>/<number>/ -> acts/<year>/<number>-<slug>/ (data/paths.json updated)."""
import csv, json, os, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import slug_of  # noqa

repo = Path(sys.argv[1])
titles = {r["key"]: r["title"] for r in csv.DictReader(open(repo / "data/laws.csv", encoding="utf8"))}
pj = json.loads((repo / "data/paths.json").read_text("utf8"))
moves = {}
for d in sorted(repo.glob("act/*/*")):
    year, num = d.parent.name, d.name
    t = titles.get(f"act-{num}") or titles.get(f"act-{int(num):04d}")
    if t is None:
        # Acts held under a name slug (data-protection etc.)
        t = next((v for k, v in titles.items() if re.search(rf"\(Act {num}\)", v)), None)
    m = re.match(r"(.*?\bAct)\b", t or "")
    slug = slug_of(m.group(1) if m else (t or "act"))
    moves[f"act/{year}/{num}"] = f"acts/{year}/{num}-{slug}"
for a, b in moves.items():
    (repo / b).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "-C", str(repo), "mv", a, b], check=True)
pj["layout"] = "acts/<year>/<number>-<slug>"
pj["since"] = "2026-11-26"
pj["note"] = ("Act folders: acts/<year>/<number>-<short name>/ since 2026-11-26 (before that act/<year>/<number>/, and "
              "before 2026-11-11 the act id); paths maps each act id to its folder.")
pj["paths"] = {k: moves.get(v, v) for k, v in pj["paths"].items()}
(repo / "data/paths.json").write_bytes((json.dumps(pj, indent=0, ensure_ascii=False) + "\n").encode("utf8"))
subprocess.run(["git", "-C", str(repo), "add", "data/paths.json"], check=True)
msg = (f"Layout: acts/<year>/<number>-<short name>/ (data/paths.json)\n\n"
       f"{len(moves)} act folders move from act/<year>/<number>/ to acts/<year>/<number>-<short name>/. Pure rename:\n"
       f"no law text changes. git log --follow follows the files; data/paths.json maps every act id to its folder.\n\n"
       f"In-force: 2026-11-26\nKind: documentation\nMoved: {len(moves)} acts\nPaths: data/paths.json\n")
env = dict(os.environ, GIT_AUTHOR_NAME="Lexifina", GIT_AUTHOR_EMAIL="ghana-law@lexifina.com",
           GIT_COMMITTER_NAME="Lexifina", GIT_COMMITTER_EMAIL="ghana-law@lexifina.com",
           GIT_AUTHOR_DATE="2026-11-26T12:00:00+0000", GIT_COMMITTER_DATE="2026-11-26T12:00:00+0000")
subprocess.run(["git", "-C", str(repo), "commit", "-q", "-F", "-"], input=msg.encode(), env=env, check=True)
print(len(moves), "moved")
