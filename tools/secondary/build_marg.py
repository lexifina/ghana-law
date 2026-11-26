"""Append Library Acts and Executive Instruments printed with marginal notes (Assembly Press prints) to ghana-law.

    python -X utf8 sec/build_marg.py <repo> [--dry]

Reader: sec/marg_read.py (provisions 1..N, Arrangement, word check). Text: the PDF's text layer; for scanned
prints that is the publisher's OCR layer (Text-source: publisher OCR). No OCR of ours.
Dates: Acts - a commencement day printed in a section, else the date of assent, else the Gazette notification
date; a commencement clause whose date cannot be read holds the Act. Executive Instruments - the day the
Instrument says it is made. Legislative and Constitutional Instruments are held (in force after 21 sitting days
of Parliament, Constitution art. 11(7); the day is not printed).
"""
import os
import hashlib, json, os, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "sec"))
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "tools"))
import marg_read as M  # noqa
import build as B  # noqa
ROOT = Path(os.environ.get("GH_ACQ", "."))
UNITS = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}
ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9,
       "tenth": 10, "eleventh": 11, "twelfth": 12, "thirteenth": 13, "fourteenth": 14, "fifteenth": 15, "sixteenth": 16,
       "seventeenth": 17, "eighteenth": 18, "nineteenth": 19, "twentieth": 20, "thirtieth": 30, "fortieth": 40,
       "fiftieth": 50, "sixtieth": 60, "seventieth": 70, "eightieth": 80, "ninetieth": 90, "hundredth": 100, "thousandth": 1000}


def ordinal(text):
    m = re.search(r"THE\s+((?:[A-Z]+[\s\-]+){1,9}?[A-Z]+)\s*\n?\s*ACT\s*\n\s*OF\s+THE\s+PARLIAMENT", text, re.I)
    if not m:
        return None
    words = re.findall(r"[a-z]+", m.group(1).lower())
    total, cur = 0, 0
    for w in words:
        if w == "and":
            continue
        if w in UNITS:
            cur += UNITS.index(w) + 1
        elif w in TENS:
            cur += TENS[w]
        elif w == "hundred":
            cur = (cur or 1) * 100
        elif w == "thousand":
            total += (cur or 1) * 1000
            cur = 0
        elif w in ORD:
            v = ORD[w]
            if v == 100:
                cur = (cur or 1) * 100
            elif v == 1000:
                total += (cur or 1) * 1000
                cur = 0
            else:
                cur += v
        else:
            return None
    return total + cur or None


def have_nums(repo):
    s = set()
    for p in Path(repo).glob("acts/*/*"):
        m = re.match(r"(\d+)-", p.name)
        if m:
            s.add(int(m.group(1)))
    return s


def titlecase(t):
    small = {"and", "of", "the", "for", "on", "to", "in", "a", "its"}
    out = []
    for i, w in enumerate(t.lower().split()):
        out.append(w if (i and w in small) else (w[:1].upper() + w[1:]))
    s = " ".join(out)
    return re.sub(r"\(([a-z])", lambda m: "(" + m.group(1).upper(), s).replace("Ii", "II").replace("C.k.", "C.K.")


def main(repo, dry):
    info = json.load(open(ROOT / "sec/marg_info.json", encoding="utf8"))
    have = have_nums(repo)
    held, items = {}, []
    for x in info:
        f = ROOT / "cache/pdf" / f"{x['uuid']}.pdf"
        raw = f.read_bytes()
        import pymupdf
        text = "\n".join(p.get_text() for p in pymupdf.open(f))
        units, err, meta = M.read(f, x["kind"])
        if err:
            held[x["name"]] = err
            continue
        ocr = x["imgs"] > 0 and not re.search(r"Word|Distiller|doPDF", x["producer"] or "")
        if x["kind"] == "act":
            num = int(x["actnum"]) if x["actnum"] else ordinal(text)
            if not num:
                held[x["name"]] = "no Act number read"
                continue
            if num in have:
                held[x["name"]] = f"Act {num} already in the repository"
                continue
            t = x["title"] or x["name"]
            ym = re.search(r"(\d{4})\s*$", t.strip(" ."))
            year = int(ym.group(1)) if ym else None
            name = titlecase(re.sub(r",?\s*\d{4}\s*$", "", t.strip(" .")).replace("TELECOMMU- NICATION", "TELECOMMUNICATION"))
            comm = None
            for k, u in units.items():
                mm = re.search(r"(?:come|comes)\s+into\s+force\s+(?:on|at)\s+([^\n.;]{4,60})", u["text"])
                if mm and k.startswith("sec-"):
                    comm = mm
            if comm:
                d = B.day(re.sub(r"(\d)\s*[“”\"']+", r"\1", comm.group(1)))
                if not d:
                    held[x["name"]] = f'commencement not read as a date: "{comm.group(0)}"'
                    continue
                inf, basis = d, f'commencement section: "{comm.group(0).strip()}"'
            elif meta.get("assent"):
                inf, basis = meta["assent"], "date of assent printed on the Act (no commencement day printed in its sections)"
            elif meta.get("gazette"):
                inf, basis = meta["gazette"], ("Gazette notification date printed on the Act (the date of assent is not "
                                               "legible in the text layer; no commencement day printed in its sections)")
            else:
                held[x["name"]] = "no date of assent, commencement or Gazette notification read"
                continue
            if not year or abs(int(inf[:4]) - year) > 1:
                held[x["name"]] = f"date {inf} does not match the year {year}"
                continue
            items.append(dict(x=x, raw=raw, units=units, meta=meta, ocr=ocr, inf=inf, basis=basis, law=f"Act {num}",
                              author=f"Act {num}", title=f"{name}, {year} (Act {num})", short=f"{name} {year}",
                              folder=f"acts/{year}/{num}-{B.slug_of(name)}", kind="law", enacted=meta.get("assent"),
                              published=meta.get("gazette")))
            have.add(num)
        else:
            if not x["inst"]:
                mi = re.search(r"\b(E|L|C)\.\s?I\.?\s*(\d{1,4})\b", x["name"])
                x["inst"] = (mi.group(1) + ".I. " + mi.group(2)) if mi else None
            if not x["inst"] or not x["inst"].startswith("E"):
                held[x["name"]] = ("Legislative/Constitutional Instrument: in force after 21 sitting days of Parliament "
                                   "(art. 11(7)); day not printed") if x["inst"] else "instrument number not read"
                continue
            if not x["made"]:
                held[x["name"]] = "Executive Instrument: no day made printed"
                continue
            num = int(re.search(r"\d+", x["inst"]).group())
            year = int(x["made"][:4])
            nm = re.sub(r"\s*,?\s*\d{4}.*$", "", x["name"]).strip()
            nm = re.sub(r"\(\s*", "(", re.sub(r"\s*\)", ")", nm)).replace("it's", "its")
            nm = re.sub(r"(\w)\(", r"\1 (", nm)
            if re.search(r"\b(19|20)\d\d\b", x["name"]) and str(year) not in x["name"]:
                held[x["name"]] = f"made {x['made']} but listed under another year"
                continue
            folder = f"subsidiary/{year}/ei-{num}-{B.slug_of(re.sub(r'\s*Instrument$', '', nm))}"
            if (Path(repo) / folder).exists():
                held[x["name"]] = "already in the repository"
                continue
            items.append(dict(x=x, raw=raw, units=units, meta=meta, ocr=ocr, inf=x["made"],
                              basis=(f"the day the Instrument says it is made ({x['made']}); an Executive Instrument "
                                     f"is not laid before Parliament"), law=f"E.I. {num} of {year}",
                              author=f"E.I. {num} of {year}", title=f"{nm}, {year} (E.I. {num})", short=f"{nm} {year}",
                              folder=folder, kind="instrument", enacted=None, published=x.get("gazette")))
    json.dump(held, open(ROOT / "sec/held_marg.json", "w", encoding="utf8"), indent=1, ensure_ascii=False)
    items.sort(key=lambda i: i["inf"])
    for it in items:
        print(it["inf"], it["folder"], len(it["units"]), "OCR" if it["ocr"] else "text", it["title"])
    for k, v in held.items():
        print("HELD", k[:70], "|", v[:100])
    if dry:
        return
    for it in items:
        d = Path(repo) / it["folder"]
        d.mkdir(parents=True)
        for k, u in it["units"].items():
            (d / f"{k}.md").write_bytes(u["text"].encode("utf8"))
        rows = "\n".join(f"| {u['title']} | [{k}.md]({k}.md) |" for k, u in sorted(it["units"].items()))
        h = it["x"]["handle"]
        verb = "passed" if it["kind"] == "law" else "made"
        (d / "README.md").write_bytes((f"# {it['title']}\n\n{it['short']} · as {verb} · in force {it['inf']} · "
                                       f"<https://repository.parliament.gh/handle/{h}>\n\n"
                                       f"| Provision | File |\n| --- | --- |\n{rows}\n").encode("utf8"))
        ts = "publisher OCR" if it["ocr"] else "publisher text layer"
        msg = (f"{it['short']} as {'enacted' if it['kind'] == 'law' else 'made'} ({it['law']})\n\n"
               f"{it['title']}: the text as {verb}, from the {'OCR layer of the scanned print' if it['ocr'] else 'text layer of the print'}"
               f" in the\nParliament of Ghana Library's repository (repository.parliament.gh). No OCR of ours.\n\n"
               f"Law: {it['law']}\nKind: {it['kind']}\n"
               + (f"Enacted: {it['enacted']}\n" if it.get("enacted") else "")
               + (f"Published: {it['published']}\n" if it.get("published") else "")
               + f"In-force: {it['inf']}\nIn-force-basis: {it['basis']}\n"
               f"Source: https://repository.parliament.gh/handle/{h}\nSource-file: {it['x']['url']}\n"
               f"Source-sha256: {hashlib.sha256(it['raw']).hexdigest()}\nText-source: {ts}\nAct: {it['short']}\n"
               f"Provisions: {len(it['units'])}\n")
        date = f"{it['inf']}T12:00:00+0000"
        env = dict(os.environ, GIT_AUTHOR_NAME=it["author"],
                   GIT_AUTHOR_EMAIL=re.sub(r"[^a-z0-9]+", "-", it["author"].lower()).strip("-") + "@repository.parliament.gh.invalid",
                   GIT_COMMITTER_NAME="Lexifina", GIT_COMMITTER_EMAIL="ghana-law@lexifina.com",
                   GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
        subprocess.run(["git", "-C", repo, "add", "--", it["folder"]], check=True)
        subprocess.run(["git", "-C", repo, "commit", "-q", "-F", "-"], input=msg.encode(), env=env, check=True)
        B.log(f"sec/build_marg {it['law']} {it['folder']} {it['inf']}")
    print(len(items), "committed;", len(held), "held")


if __name__ == "__main__":
    main(sys.argv[1], "--dry" in sys.argv)
