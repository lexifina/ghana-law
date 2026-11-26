"""Append Library items that tools/build.py skipped (titles without "ACT N", Executive Instruments) to ghana-law main.

    python -X utf8 sec/build_inst.py <repo> [--dry]

Same reader and checks as tools/build.py (sections/regulations/paragraphs 1..N without a gap, Arrangement count,
word check), with "Regulation N—" and "Paragraph N—" headings allowed. Dates: see each item's basis.
Legislative and Constitutional Instruments are not taken: they come into force after 21 sitting days of
Parliament (Constitution, art. 11(7)) and the day is not printed on them.
"""
import os
import hashlib, json, os, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "tools"))
import build as B  # noqa
B.SEC = re.compile(r"^\s*(?:Section|Regulation|Rule|Paragraph)\s+(\d{1,3}[A-Z]?)\s*[\u2014\u2013\-]+\s*(.*)$")
ROOT = Path(os.environ.get("GH_ACQ", "."))

ITEMS = [
    # handle, folder, title, short, law, author, inf, basis, enacted, published
    ("2106", "acts/1994/{n}-locksmiths-licensing", "Locksmiths (Licensing) Act, 1994 (Act {n})", "Locksmiths (Licensing) Act 1994",
     "Act {n}", "Act {n}", "1994-12-22", "date of assent printed on the Act (no later commencement day printed in its sections)",
     "1994-12-22", "1994-12-30"),
]


def pdf_of(handle):
    for l in open(ROOT / "catalogue.jsonl", encoding="utf8"):
        r = json.loads(l)
        if r["handle"].endswith("/" + handle):
            for b in r["bitstreams"]:
                f = ROOT / "cache/pdf" / f"{b['uuid']}.pdf"
                if b["bundle"] == "ORIGINAL" and f.exists():
                    return r, b, f
    raise SystemExit("no pdf " + handle)


def front(pdf):
    """Enabling words of an instrument: from the line after the title to the first heading."""
    import pymupdf
    L = B.lines_of(pymupdf.open(pdf))
    i = next(k for k, s in enumerate(L) if B.SEC.match(s))
    j = next((k for k, s in enumerate(L[:i]) if re.match(r"^IN\s+exercise", s)), None)
    return B.paras(L[j:i]) if j is not None else None


def main(repo, dry):
    items = json.load(open(ROOT / "sec/inst_items.json", encoding="utf8"))
    out = subprocess.run(["git", "-C", repo, "log", "--format=%at", "--max-count=4000"], capture_output=True, text=True)
    pre = max([int(x) for x in out.stdout.split() if x.isdigit() and int(x) < 86400] + [1000])
    for it in items:
        r, b, f = pdf_of(it["handle"])
        raw = f.read_bytes()
        units, err, meta = B.read(raw)
        if err:
            print("HOLD", it["title"], err)
            continue
        if "preamble" not in units:
            fr = front(f)
            if fr:
                units["preamble"] = {"title": "Enabling words", "text": fr + "\n"}
        d = Path(repo) / it["folder"]
        print(it["inf"], it["folder"], len(units), meta.get("words"))
        if dry or d.exists():
            continue
        d.mkdir(parents=True)
        for k, u in units.items():
            (d / f"{k}.md").write_bytes(u["text"].encode("utf8"))
        rows = "\n".join(f"| {u['title']} | [{k}.md]({k}.md) |" for k, u in sorted(units.items()))
        (d / "README.md").write_bytes((f"# {it['title']}\n\n{it['short']} · as made · in force {it['inf']} · "
                                       f"<https://repository.parliament.gh/handle/{r['handle']}>\n\n"
                                       f"| Provision | File |\n| --- | --- |\n{rows}\n").encode("utf8"))
        msg = (f"{it['short']} as {'enacted' if it['kind'] == 'law' else 'made'} ({it['law']})\n\n"
               f"{it['title']}: the text as {'passed' if it['kind'] == 'law' else 'made'}, from the text layer of the "
               f"Parliament of Ghana Library's\nedition (repository.parliament.gh). No OCR.\n\n"
               f"Law: {it['law']}\nKind: {it['kind']}\n"
               + (f"Enacted: {it['enacted']}\n" if it.get("enacted") else "")
               + (f"Published: {it['published']}\n" if it.get("published") else "")
               + f"In-force: {it['inf']}\nIn-force-basis: {it['basis']}\n"
               f"Source: https://repository.parliament.gh/handle/{r['handle']}\nSource-file: {b['url']}\n"
               f"Source-sha256: {hashlib.sha256(raw).hexdigest()}\nText-source: publisher text layer\nAct: {it['short']}\n"
               f"Provisions: {len(units)}\n")
        date = f"{it['inf']}T12:00:00+0000"
        if it["inf"] < "1970-01-02":
            pre += 1
            date = f"@{pre} +0000"
            msg = msg.replace("\n\nLaw: ", "\n\nGit cannot store a date before 1970, so this commit is dated 1 January 1970, "
                              "a second after the one\nbefore it. The day the change took effect is in the In-force "
                              "trailer, which tools/on.py reads.\n\nLaw: ", 1)
        env = dict(os.environ, GIT_AUTHOR_NAME=it["author"],
                   GIT_AUTHOR_EMAIL=re.sub(r"[^a-z0-9]+", "-", it["author"].lower()).strip("-") + "@repository.parliament.gh.invalid",
                   GIT_COMMITTER_NAME="Lexifina", GIT_COMMITTER_EMAIL="ghana-law@lexifina.com",
                   GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
        subprocess.run(["git", "-C", repo, "add", "--", it["folder"]], check=True)
        subprocess.run(["git", "-C", repo, "commit", "-q", "-F", "-"], input=msg.encode(), env=env, check=True)
        B.log(f"sec/build_inst {it['law']} {it['folder']} {it['inf']}")
        print("committed", it["folder"])


if __name__ == "__main__":
    main(sys.argv[1], "--dry" in sys.argv)
