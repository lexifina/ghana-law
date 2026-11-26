"""Bring the 1992 Constitution (as made, 1993; as amended by Act 527, 1996) from the preview branch onto main.

    python -X utf8 sec/const_publish.py <repo> [--dry]

Text: the preview branch's files (OSP's copy "as Amended to 1996", the Audit Service copy for the nine passages
Act 527 changed), with two Part headings that had been caught at the end of Articles 111 and 143 removed.
Cross-check: Constitute Project's text of the 1992 Constitution (rev. 1996), word by word per article, and the
scanned official print with Act 527 on WIPO Lex (publisher OCR layer) for the articles where the two differ.
"""
import os
import io, os, re, shutil, subprocess, sys, zipfile
from pathlib import Path

STRIP = {"art-111.md": "Summoning, Dissolution, etc.",
         "art-143.md": "Appointment, retirement and removal of Justices of Superior Courts and chairmen and other members of Regional Tribunals."}
CHECK = ("Cross-checked against two other copies: Constitute Project's text of the Constitution (rev. 1996)\n"
         "agrees word for word in 240 of 299 articles and in 286 to 99% or more; where they differ (spelling such\n"
         "as practise/practice, a duplicated clause in Constitute's Article 21, and Article 211(a), which Constitute\n"
         "gives in its pre-1996 wording), the scanned official print of the Constitution and of Act 527 on WIPO Lex\n"
         "(Adobe OCR layer) was read and agrees with this text. Two Part headings that the preview branch had\n"
         "caught at the end of Articles 111 and 143 are left out.\n\n")


def main(repo, dry):
    for ref, extra in (("dc64b3b", "https://www.constituteproject.org/constitution/Ghana_1996"),
                       ("db1c7cd", "https://www.constituteproject.org/constitution/Ghana_1996")):
        z = zipfile.ZipFile(io.BytesIO(subprocess.run(["git", "-C", repo, "archive", "--format=zip", ref, "constitution/"],
                                                      capture_output=True, check=True).stdout))
        msg = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%B", ref], capture_output=True, text=True,
                             encoding="utf8").stdout.rstrip() + "\n"
        an, ae, ad = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%an%x00%ae%x00%aI", ref],
                                    capture_output=True, text=True, encoding="utf8").stdout.strip().split("\x00")
        files = {n: z.read(n).decode("utf8") for n in z.namelist() if n.endswith(".md")}
        for name, head in STRIP.items():
            k = f"constitution/{name}"
            lines = files[k].rstrip("\n").split("\n")
            assert lines[-1].strip() == head, (k, lines[-1])
            files[k] = "\n".join(lines[:-1]) + "\n"
        print(ref, len(files), "files", ad)
        if dry:
            continue
        d = Path(repo) / "constitution"
        if d.exists():
            shutil.rmtree(d)
        for n, t in files.items():
            p = Path(repo) / n
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(t.encode("utf8"))
        head, _, trailers = msg.partition("\nLaw: ")
        body = head.rstrip() + "\n\n" + CHECK + "Law: " + trailers
        body = body.rstrip() + "\n" + ("Source-status: secondary copy (Office of the Special Prosecutor, "
                                       "https://osp.gov.gh/media/Resources/Ghana_Constitution.pdf)\n"
                                       "Text-source: secondary text layer (OSP compilation)\n"
                                       f"Checked-against: {extra}\n"
                                       "Checked-against: https://www.wipo.int/wipolex/en/legislation/details/9414\n")
        env = dict(os.environ, GIT_AUTHOR_NAME=an, GIT_AUTHOR_EMAIL=ae.replace("ghalii.invalid", "ghana-law.invalid"),
                   GIT_COMMITTER_NAME="Lexifina", GIT_COMMITTER_EMAIL="ghana-law@lexifina.com",
                   GIT_AUTHOR_DATE=ad, GIT_COMMITTER_DATE=ad)
        subprocess.run(["git", "-C", repo, "add", "-A", "--", "constitution"], check=True)
        subprocess.run(["git", "-C", repo, "commit", "-q", "-F", "-"], input=body.encode(), env=env, check=True)
        print("committed", ref)


if __name__ == "__main__":
    main(sys.argv[1], "--dry" in sys.argv)
