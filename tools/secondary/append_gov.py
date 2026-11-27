"""Append Acts as passed (or consolidations) read from government-hosted or Library PDFs to ghana-law main.

    python -X utf8 sec/append_gov.py <repo> <job.json> [--dry]

job item: {pdf, reader: build|marg|wipo, folder, title, short, law, enacted, published, inf, basis, source,
source_file, publisher, mode: passed|consolidation, includes?, secondary?: "<name>"}.
One commit per item, noon Africa/Accra (UTC+0) on the in-force day. Pre-1970 days: 1970-01-01 stamp (one second
apart), real day in In-force. No OCR of ours.
"""
import os
import hashlib, json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "tools"))
import build as B, marg_read as MR, wipo_read as W  # noqa

pre70 = [0]


def read(it):
    if it["reader"] == "marg":
        u, e, m = MR.read(it["pdf"], "act")
        m.pop("dropped", None)
        return u, e, m
    if it["reader"] == "wipo":
        return W.read(it["pdf"])
    return B.read(Path(it["pdf"]).read_bytes())


def main(repo, job, dry):
    last = subprocess.run(["git", "-C", repo, "log", "--format=%at"], capture_output=True, text=True).stdout.split()
    pre70[0] = max([int(x) for x in last if int(x) < 86400] or [0])
    for it in json.load(open(job, encoding="utf-8-sig")):
        units, err, meta = read(it)
        if err or not units:
            print("HOLD", it["title"], err)
            continue
        d = Path(repo) / it["folder"]
        print(it["inf"], it["folder"], len(units), "units; assent", meta.get("assent"), "gazette", meta.get("gazette"))
        if dry:
            continue
        if d.exists():
            print("exists, skipped", d)
            continue
        d.mkdir(parents=True)
        for k, u in units.items():
            (d / f"{k}.md").write_bytes(u["text"].encode("utf8"))
        rows = "\n".join(f"| {u['title']} | [{k}.md]({k}.md) |" for k, u in sorted(units.items()))
        sec = it.get("secondary")
        what = "as passed" if it["mode"] == "passed" else f"consolidation ({it.get('includes', '')})"
        src_note = f"secondary copy: {sec}" if sec else f"copy published by {it['publisher']}"
        (d / "README.md").write_bytes((f"# {it['title']}\n\n{it['short']} Â· {what} Â· in force {it['inf']} Â· "
                                       f"{src_note} <{it['source']}>\n\n"
                                       f"| Provision | File |\n| --- | --- |\n{rows}\n").encode("utf8"))
        sha = hashlib.sha256(Path(it["pdf"]).read_bytes()).hexdigest()
        if it["mode"] == "passed":
            subj = f"{it['short']} as enacted ({it['law']})"
            body = (f"{it['title']}: the text as passed, from the text layer of the copy published by\n"
                    f"{it['publisher']}. No OCR of ours.\n\n")
            kind = "law"
            law = it["law"]
        else:
            subj = f"{it['short']}: consolidation {it['includes']} ({it['law']})"
            body = (f"{it['title']}: the text {it['includes']}, from the text layer of the copy published by\n"
                    f"{it['publisher']}. No OCR of ours.\n\n")
            kind = "consolidation"
            law = f"{it['law']} (consolidation)"
        inf = it["inf"]
        if inf < "1970-01-01":
            subj += f", in force {inf}"
            pre70[0] += 1
            date = f"@{pre70[0]} +0000"
        else:
            date = f"{inf}T12:00:00+0000"
        msg = (f"{subj}\n\n{body}Law: {law}\nKind: {kind}\n"
               + (f"Enacted: {it['enacted']}\n" if it.get("enacted") else "")
               + (f"Published: {it['published']}\n" if it.get("published") else "")
               + f"In-force: {inf}\nIn-force-basis: {it['basis']}\n"
               f"Source: {it['source']}\nSource-file: {it['source_file']}\nSource-sha256: {sha}\n"
               + (f"Source-status: secondary copy ({sec}, {it['source']})\n" if sec else "")
               + f"Text-source: {it.get('text_source', 'publisher text layer')}\nAct: {it['short']}\n"
               f"Provisions: {len(units)}\n")
        num = it["law"].split()[-1]
        env = dict(os.environ, GIT_AUTHOR_NAME=it["law"], GIT_AUTHOR_EMAIL=f"act-{num}@ghana-law.invalid",
                   GIT_COMMITTER_NAME="Lexifina", GIT_COMMITTER_EMAIL="ghana-law@lexifina.com",
                   GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
        subprocess.run(["git", "-C", repo, "add", "--", it["folder"]], check=True)
        subprocess.run(["git", "-C", repo, "commit", "-q", "-F", "-"], input=msg.encode(), env=env, check=True)
        print("committed", it["folder"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], "--dry" in sys.argv)
