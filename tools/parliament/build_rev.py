"""Add the Library's Revised Editions (consolidations) that have a text layer, as consolidated versions.

    python -X utf8 tools/build_rev.py <repo> [--dry]

The Revised Editions print no date of their own. Each is dated by the latest law it says it includes
("As amended by ..."): that law's date of assent from this repository (data/laws.csv) or, failing that, the
repository catalogue's date issued for it. An edition naming no amending law is dated by the date of assent
printed on it. Editions marked "As repealed by" are not taken. Same reader and checks as build.py.
"""
import csv, hashlib, json, os, re, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as B  # noqa

ROOT = B.ROOT


def main(repo, dry):
    import pymupdf
    laws = {r["key"]: r for r in csv.DictReader(open(Path(repo) / "data/laws.csv", encoding="utf8"))}
    cat_dates = {}
    for l in open(ROOT / "catalogue.jsonl", encoding="utf8"):
        r = json.loads(l)
        m = B.ACT_RE.search(re.sub(r"\s+", " ", r["name"]))
        iss = (r["md"].get("dc.date.issued") or [""])[0]
        if m and len(iss) == 10 and not re.search(r"Bill", r["name"]):
            cat_dates.setdefault(int(m.group("num")), iss)
    cat = B.catalogue()
    folders = {}
    for d in Path(repo).glob("acts/*/*"):
        m = re.match(r"(\d+)-", d.name)
        if m:
            folders[int(m.group(1))] = d
    items, held = [], {}
    for num, cands in sorted(cat.items()):
        for c in [c for c in cands if c["revised"]]:
            for s in c["pdfs"]:
                f = ROOT / "cache/pdf" / f"{s['uuid']}.pdf"
                if not f.exists():
                    continue
                b = f.read_bytes()
                try:
                    d = pymupdf.open(stream=b, filetype="pdf")
                    head = "".join(p.get_text() for p in d)[:4000]
                except Exception:
                    continue
                if len(head.strip()) < 300:
                    continue
                if re.search(r"As repealed by", head, re.I):
                    held[num] = (c["name"], "Revised Edition marked as repealed")
                    continue
                try:
                    units, err, meta = B.read(b)
                except Exception as e:
                    units, err, meta = None, f"reader error {e}", {}
                if not units:
                    held[num] = (c["name"], f"Revised Edition: {err}")
                    continue
                am = re.search(r"As [Aa]mended by(.*?)ARRANGEMENT OF SECTIONS", head, re.S)
                amenders = re.findall(r"\((ACT|PNDCL|NRCD|NLCD|SMCD|AFRCD)\s*\.?\s*(\d+)\)", am.group(1).upper()) if am else []
                dates, unknown = [], []
                for kind, n in amenders:
                    dt = None
                    if kind == "ACT":
                        dt = next((r["enacted"] for r in laws.values()
                                   if re.fullmatch(rf"Act {int(n)}( of \d{{4}})?", r["label"]) and r["enacted"]), None)
                        dt = dt or cat_dates.get(int(n))
                    (dates if dt else unknown).append((dt, f"{kind.title() if kind == 'ACT' else kind} {n}"))
                if unknown:
                    held[num] = (c["name"], "Revised Edition: no date found for " + ", ".join(u[1] for u in unknown))
                    continue
                if dates:
                    dt, by = max(dates)
                    basis = (f"revised-edition: the Library's Revised Edition (a consolidation) prints no date; dated by the "
                             f"latest law it includes, {by} (date of assent {dt})")
                elif meta.get("assent"):
                    dt = meta["assent"]
                    basis = ("revised-edition: the Library's Revised Edition (a consolidation) prints no date and names no "
                             "amending law; dated by the date of assent printed on it")
                else:
                    held[num] = (c["name"], "Revised Edition: no date")
                    continue
                year = c["year"] or int((meta.get("assent") or dt)[:4])
                folder = folders.get(num) or (Path(repo) / f"acts/{year}/{num}-{B.slug_of(c['title'])}")
                items.append(dict(num=num, year=year, title=f"{c['title']}, {year} (Act {num})", short=f"{c['title']} {year}",
                                  handle=c["handle"], url=s["url"], sha=hashlib.sha256(b).hexdigest(), units=units,
                                  inf=dt, basis=basis, folder=folder, amenders=[a[1] for a in dates]))
                break
            else:
                continue
            break
    items.sort(key=lambda x: (x["inf"], x["num"]))
    (ROOT / "held_revised.json").write_text(json.dumps({str(k): v for k, v in held.items()}, indent=1), "utf8")
    if dry:
        for it in items:
            print(it["inf"], it["folder"].relative_to(repo), len(it["units"]), it["amenders"])
        print(len(items), "ready;", len(held), "held")
        for k, v in held.items():
            print("HELD", k, *v)
        return
    out = subprocess.run(["git", "-C", repo, "log", "--format=%at", "--max-count=3000"], capture_output=True, text=True)
    pre = max([int(x) for x in out.stdout.split() if x.isdigit() and int(x) < 86400] + [1000])
    for it in items:
        d = it["folder"]
        if d.exists():
            for f in d.glob("*.md"):
                if f.name != "README.md" and f.stem not in it["units"]:
                    f.unlink()
        d.mkdir(parents=True, exist_ok=True)
        for k, u in it["units"].items():
            (d / f"{k}.md").write_bytes(u["text"].encode("utf8"))
        rows = "\n".join(f"| {u['title']} | [{k}.md]({k}.md) |" for k, u in sorted(it["units"].items()))
        (d / "README.md").write_bytes((f"# {it['title']}\n\n{it['short']} · Revised Edition (consolidation) · from {it['inf']} · "
                                       f"<https://repository.parliament.gh/handle/{it['handle']}>\n\n"
                                       f"| Provision | File |\n| --- | --- |\n{rows}\n").encode("utf8"))
        inc = ("Laws it includes: " + ", ".join(it["amenders"]) + ".\n\n") if it["amenders"] else ""
        msg = (f"{it['short']}: Revised Edition, a consolidation (Act {it['num']})\n\n"
               f"{it['title']}: the Parliament of Ghana Library's Revised Edition, a consolidation of the Act with the\n"
               f"amendments it names, from the PDF text layer (repository.parliament.gh). No OCR.\n\n{inc}"
               f"Law: Act {it['num']} (Revised Edition)\nKind: consolidation\nIn-force: {it['inf']}\n"
               f"In-force-basis: {it['basis']}\n"
               f"Source: https://repository.parliament.gh/handle/{it['handle']}\nSource-file: {it['url']}\n"
               f"Source-sha256: {it['sha']}\nText-source: publisher text layer (Revised Edition)\nAct: {it['short']}\n"
               f"Provisions: {len(it['units'])}\n")
        date = f"{it['inf']}T12:00:00+0000"
        if it["inf"] < "1970-01-02":
            pre += 1
            date = f"@{pre} +0000"
            msg = msg.replace("\n\nLaw: ", "\n\nGit cannot store a date before 1970, so this commit is dated 1 January 1970, "
                              "a second after the one\nbefore it. The day is in the In-force trailer.\n\nLaw: ", 1)
        env = dict(os.environ, GIT_AUTHOR_NAME="Parliament of Ghana Library",
                   GIT_AUTHOR_EMAIL="library@repository.parliament.gh.invalid",
                   GIT_COMMITTER_NAME="Lexifina", GIT_COMMITTER_EMAIL="ghana-law@lexifina.com",
                   GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
        subprocess.run(["git", "-C", repo, "add", "-A", "--", str(d.relative_to(repo))], check=True)
        subprocess.run(["git", "-C", repo, "commit", "-q", "-F", "-"], input=msg.encode(), env=env, check=True)
        B.log(f"revised Act {it['num']} {d.relative_to(repo)} {it['inf']}")
    print(len(items), "committed;", len(held), "held")


if __name__ == "__main__":
    main(sys.argv[1], "--dry" in sys.argv)
