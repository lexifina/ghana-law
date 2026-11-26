"""Append secondary-source consolidations to ghana-law main (one commit each).

    python -X utf8 sec/append_sec.py <repo> <job.json> [--dry]

job.json: list of {pdf, reader: "wipo", folder, title, short, law, inf, basis, source, source_file, source_name,
author, author_email, text_source, includes}. Every commit carries Source-status: secondary copy (...).
"""
import os
import hashlib, json, os, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import wipo_read as W  # noqa


def main(repo, job, dry):
    for it in json.load(open(job, encoding="utf8")):
        if it.get("reader") == "marg":
            import marg_read as MR
            units, err, meta = MR.read(it["pdf"], "act")
            meta.pop("dropped", None)
        else:
            units, err, meta = W.read(it["pdf"])
        if err:
            print("HOLD", it["title"], err)
            continue
        d = Path(repo) / it["folder"]
        print(it["inf"], it["folder"], len(units), "units", meta["sections"], "sections; words", meta["words"])
        if dry:
            continue
        if d.exists():
            print("exists, skipped", d)
            continue
        d.mkdir(parents=True)
        for k, u in units.items():
            (d / f"{k}.md").write_bytes(u["text"].encode("utf8"))
        rows = "\n".join(f"| {u['title']} | [{k}.md]({k}.md) |" for k, u in sorted(units.items()))
        (d / "README.md").write_bytes((f"# {it['title']}\n\n{it['short']} · consolidation ({it.get('includes', '')}) · from "
                                       f"{it['inf']} · secondary copy: {it['source_name']} <{it['source']}>\n\n"
                                       f"| Provision | File |\n| --- | --- |\n{rows}\n").encode("utf8"))
        sha = hashlib.sha256(Path(it["pdf"]).read_bytes()).hexdigest()
        if it.get("mode") == "passed":
            (d / "README.md").write_bytes((f"# {it['title']}\n\n{it['short']} · as passed · in force {it['inf']} · "
                                           f"secondary copy: {it['source_name']} <{it['source']}>\n\n"
                                           f"| Provision | File |\n| --- | --- |\n{rows}\n").encode("utf8"))
            msg = (f"{it['short']} as enacted ({it['law']})\n\n"
                   f"{it['title']}: the text as passed, from the text layer of {it['source_name']}'s copy of the\n"
                   f"Assembly Press print. The Parliament of Ghana Library has no usable copy. No OCR.\n\n"
                   f"Law: {it['law']}\nKind: law\nEnacted: {it['enacted']}\n"
                   + (f"Published: {it['published']}\n" if it.get("published") else "")
                   + f"In-force: {it['inf']}\nIn-force-basis: {it['basis']}\n"
                   f"Source: {it['source']}\nSource-file: {it['source_file']}\nSource-sha256: {sha}\n"
                   f"Source-status: secondary copy ({it['source_name']}, {it['source']})\n"
                   f"Text-source: {it['text_source']}\nAct: {it['short']}\nProvisions: {len(units)}\n")
        else:
          msg = (f"{it['short']}: consolidation {it['includes']} ({it['law']})\n\n"
               f"{it['title']}: the text {it['includes']}, from the text layer of {it['source_name']}'s copy.\n"
               f"No official copy with a text layer was found (the Parliament of Ghana Library holds this Act only as\n"
               f"a scanned Revised Edition). No OCR.\n\n"
               f"Law: {it['law']} (consolidation)\nKind: consolidation\nIn-force: {it['inf']}\n"
               f"In-force-basis: {it['basis']}\n"
               f"Source: {it['source']}\nSource-file: {it['source_file']}\nSource-sha256: {sha}\n"
               f"Source-status: secondary copy ({it['source_name']}, {it['source']})\n"
               f"Text-source: {it['text_source']}\nAct: {it['short']}\nProvisions: {len(units)}\n")
        date = f"{it['inf']}T12:00:00+0000"
        env = dict(os.environ, GIT_AUTHOR_NAME=it["author"], GIT_AUTHOR_EMAIL=it["author_email"],
                   GIT_COMMITTER_NAME="Lexifina", GIT_COMMITTER_EMAIL="ghana-law@lexifina.com",
                   GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
        subprocess.run(["git", "-C", repo, "add", "--", it["folder"]], check=True)
        subprocess.run(["git", "-C", repo, "commit", "-q", "-F", "-"], input=msg.encode(), env=env, check=True)
        print("committed", it["folder"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], "--dry" in sys.argv)
