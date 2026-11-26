"""Append Acts of Parliament of Ghana from the Parliament of Ghana Library repository to ghana-law main.

    python -X utf8 tools/build.py <repo> [--dry] [--limit N]

Layout: acts/<year>/<number>-<slug>/ ; one file per section (sec-NNN.md), preamble.md, schedule-NN.md.
One commit per Act (the Act as passed), dated noon Africa/Accra (UTC+0) on its in-force day.
Text: the PDF text layer of the Library's typed edition (no OCR). A PDF is taken only if
  - it has a text layer (>= 150 characters per page on average),
  - its body sections are headed "Section N—Title" and run 1..N without a gap (lettered inserts allowed),
  - the number of sections equals the Arrangement of Sections where one is printed,
  - every word of the body is kept in a file (word count check).
Revised / consolidated editions ("Revised", "As amended by") are not taken (Acts as passed only).
Everything not taken is listed in held.json with the reason.
"""
import glob, hashlib, json, os, re, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = open(ROOT / "progress.log", "a", encoding="utf8", buffering=1)
MONTHS = {m: i for i, m in enumerate("january february march april may june july august september october "
                                     "november december".split(), 1)}
STOP = {"the", "of", "and", "act", "a", "for", "on", "to", "in"}
SEC = re.compile(r"^\s*Section\s+(\d{1,3}[A-Z]?)\s*[—–\-]+\s*(.*)$")
SCHED = re.compile(r"^\s*((?:FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH|ELEVENTH|TWELFTH)\s+)?"
                   r"SCHEDULES?\s*(?:[—–\-].*)?$")


def log(m):
    LOG.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + m + "\n")


def day(s):
    m = re.search(r"(\d{1,2})\s*(?:st|nd|rd|th|ST|ND|RD|TH)?\s+(?:day\s+of\s+)?([A-Za-z]+)\s*,?\s+(\d{4})", s or "")
    if m and m.group(2).lower() in MONTHS:
        try:
            import datetime
            return datetime.date(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1))).isoformat()
        except ValueError:
            return None
    return None


def slug_of(title):
    t = re.sub(r",?\s*\(?\s*\d{4}\s*\)?.*$", "", title.strip())
    words = re.findall(r"[a-z0-9]+", t.lower().replace("'", ""))
    w = [x for x in words if x not in STOP] or words
    return "-".join(w)[:60].strip("-") or "act"


def title_case_name(name):
    n = re.sub(r"\s+", " ", name).strip()
    n = re.sub(r"\s*\(\s*", " (", n).replace(" )", ")")
    return n


ACT_RE = re.compile(r"^(?P<title>.*?\bAct)\b\s*[,.]?\s*(?P<year>(?:18|19|20)\d\d)?\b.*?\bACT\s*\.?\s*(?P<num>\d{1,4})\b",
                    re.I)


def catalogue():
    out = {}
    for l in open(ROOT / "catalogue.jsonl", encoding="utf8"):
        r = json.loads(l)
        n = re.sub(r"\s+", " ", r["name"]).strip()
        if re.search(r"\bBill\b|Report of|Memorandum", n, re.I):
            continue
        m = ACT_RE.search(n)
        if not m:
            continue
        num = int(m.group("num"))
        revised = bool(re.search(r"revised|as amended", n, re.I))
        issued = (r["md"].get("dc.date.issued") or [""])[0]
        year = int(m.group("year")) if m.group("year") else (int(issued[:4]) if issued[:4].isdigit() else None)
        pdfs = [s for s in r["bitstreams"] if s["bundle"] == "ORIGINAL" and s["name"].lower().endswith(".pdf")]
        out.setdefault(num, []).append({"num": num, "year": year, "title": m.group("title").strip(" ,."),
                                        "name": n, "revised": revised, "handle": r["handle"], "pdfs": pdfs,
                                        "uuid": r["uuid"]})
    return out


def lines_of(doc):
    out = []
    for pg in doc:
        for ln in pg.get_text().split("\n"):
            s = ln.replace(" ", " ").replace("", "").rstrip()
            if re.fullmatch(r"\s*\d{1,3}\s*", s):  # page numbers
                continue
            out.append(s.strip())
    return out


def paras(lines):
    out, cur = [], ""
    for s in lines:
        if not s:
            continue
        new = bool(re.match(r"^(\(\w{1,5}\)|\d+\.\s|\[)", s)) or not cur or re.search(r"[.;:]\s*$", cur)
        if new and cur:
            out.append(cur)
            cur = s
        else:
            cur = (cur + " " + s).strip() if cur else s
    if cur:
        out.append(cur)
    return "\n\n".join(re.sub(r"\s+", " ", p).strip() for p in out)


def read(pdf_bytes):
    import pymupdf
    d = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    raw = "".join(p.get_text() for p in d)
    if len(raw.strip()) < 150 * max(1, d.page_count) * 0.5 and len(raw.strip()) < 150 * d.page_count:
        return None, "image-only PDF (no text layer; no OCR)", {}
    L = lines_of(d)
    joined = "\n".join(L)
    meta = {}
    m = re.search(r"DATE\s+OF\s+ASSENT\s*:?\s*([^\n]{6,60})", joined, re.I)
    meta["assent"] = day(m.group(1)) if m else None
    m = re.search(r"Gazette\s+[Nn]otification\s*:?\s*([^\n]{6,60})", joined)
    meta["gazette"] = day(m.group(1)) if m else None
    heads = [i for i, s in enumerate(L) if SEC.match(s)]
    if not heads:
        return None, 'no "Section N—" headings in the text layer', meta
    # arrangement count
    arr = None
    try:
        a0 = next(i for i, s in enumerate(L) if re.match(r"ARRANGEMENT\s+OF\s+SECTIONS", s, re.I))
        a1 = next(i for i, s in enumerate(L) if i > a0 and re.search(r"OF THE PARLIAMENT OF|^AN ACT\b|ENTITLED", s))
        nums = [int(x) for x in re.findall(r"^(\d{1,3})\s*\.", "\n".join(L[a0:a1]), re.M)]
        arr = max(nums) if nums else None
    except StopIteration:
        pass
    # preamble: from "THE ... ACT / OF THE PARLIAMENT" heading (or "AN ACT") to the first section
    first = heads[0]
    p0 = None
    for i in range(first - 1, -1, -1):
        if re.match(r"^AN\s+ACT\b", L[i]):
            p0 = i
            break
    units = {}
    if p0 is not None:
        units["preamble"] = {"title": "Preamble", "text": paras(L[p0:first])}
    # sections and trailing schedules
    sec_nums = []
    for k, i in enumerate(heads):
        j = heads[k + 1] if k + 1 < len(heads) else len(L)
        m = SEC.match(L[i])
        n, ttl = m.group(1), m.group(2).strip()
        body = L[i + 1:j]
        tail = []
        if k + 1 == len(heads):  # split schedules / gazette line off the last section
            for q, s in enumerate(body):
                if SCHED.match(s) and s.upper() == s:
                    tail = body[q:]
                    body = body[:q]
                    break
        key = f"sec-{int(re.match(r'\d+', n).group()):03d}" + (n[-1].lower() if n[-1].isalpha() else "")
        if key in units:
            return None, f"section {n} appears twice", meta
        sec_nums.append(n)
        units[key] = {"title": f"Section {n}", "text": f"# {n}. {ttl}\n" + paras(body) + "\n"}
    if tail:
        sch, cur = [], None
        for s in tail:
            if SCHED.match(s) and s.upper() == s:
                cur = [s]
                sch.append(cur)
            elif cur is not None:
                cur.append(s)
        for q, block in enumerate(sch, 1):
            units[f"schedule-{q:02d}"] = {"title": f"Schedule {q}", "text": f"# {block[0]}\n" + paras(block[1:]) + "\n"}
    plain = [int(x) for x in sec_nums if x.isdigit()]
    if plain != list(range(1, len(plain) + 1)):
        return None, f"sections not numbered 1..N without a gap ({len(plain)} read, last {plain[-1] if plain else None})", meta
    if arr and arr != len(plain):
        return None, f"sections read {len(plain)} vs Arrangement {arr}", meta
    # word check: every word from the first section heading on is in a file
    src_words = len(re.findall(r"\w+", "\n".join(L[first:]))) - len(heads)  # the word "Section" of each heading
    kept = len(re.findall(r"\w+", " ".join(u["text"] for k, u in units.items() if k != "preamble")))
    meta["words"] = (src_words, kept)
    if kept < src_words:
        return None, f"word check: {src_words - kept} words not kept", meta
    m = None
    for k in sorted(units):
        if k.startswith("sec-"):
            mm = re.search(r"(?:come|comes)\s+into\s+force\s+on\s+(?:the\s+)?([^\n.;]{6,40}\d{4})", units[k]["text"])
            if mm and "commence" in units[k]["text"][:80].lower():
                m = mm
    meta["commencement"] = day(m.group(1)) if m else None
    meta["commencement_text"] = m.group(0) if m else None
    return units, None, meta


def existing(repo):
    have = set()
    for p in list(Path(repo).glob("act/*/*")) + list(Path(repo).glob("acts/*/*")):
        m = re.match(r"(\d+)", p.name)
        if m:
            have.add(int(m.group(1)))
    return have


def build(repo, dry=False, limit=0):
    import pymupdf  # noqa
    cat = catalogue()
    have = existing(repo) | {527, 832, 843, 992, 1038, 1045}
    held_p = ROOT / "held.json"
    held = json.loads(held_p.read_text("utf8")) if held_p.exists() else {}
    items = []
    for num, cands in sorted(cat.items()):
        if num in have:
            continue
        orig = [c for c in cands if not c["revised"]]
        if not orig:
            held[str(num)] = {"title": cands[0]["name"], "why": "only a Revised/consolidated edition in the repository"}
            continue
        got, why = None, []
        for c in orig:
            for s in c["pdfs"]:
                f = ROOT / "cache" / "pdf" / f"{s['uuid']}.pdf"
                if not f.exists():
                    why.append("PDF not fetched yet")
                    continue
                b = f.read_bytes()
                try:
                    units, err, meta = read(b)
                except Exception as e:
                    units, err, meta = None, f"reader error {type(e).__name__}: {str(e)[:80]}", {}
                if units:
                    got = (c, s, b, units, meta)
                    break
                why.append(err)
            if got:
                break
        if not got:
            if not any("not fetched" in w for w in why):
                held[str(num)] = {"title": orig[0]["name"], "why": "; ".join(sorted(set(why))) or "no PDF"}
            continue
        c, s, b, units, meta = got
        held.pop(str(num), None)
        year = c["year"]
        assent = meta.get("assent")
        if assent and year and assent[:4] != str(year) and int(assent[:4]) - year not in (0, 1):
            held[str(num)] = {"title": c["name"], "why": f"assent {assent} does not match the year {year}"}
            continue
        if not year and assent:
            year = int(assent[:4])
        if not year:
            held[str(num)] = {"title": c["name"], "why": "no year"}
            continue
        if meta.get("commencement") and assent and meta["commencement"] >= assent:
            inf, basis = meta["commencement"], f'commencement section: "{meta["commencement_text"]}"'
        elif assent:
            inf, basis = assent, "date of assent printed on the Act (no later commencement day printed in its sections)"
        elif meta.get("gazette"):
            inf, basis = meta["gazette"], "Gazette notification date printed on the Act (no date of assent printed)"
        else:
            held[str(num)] = {"title": c["name"], "why": "no date of assent, commencement or Gazette notification printed"}
            continue
        title = f"{c['title']}, {year} (Act {num})"
        items.append(dict(num=num, year=year, title=title, short=f"{c['title']} {year}", handle=c["handle"],
                          url=s["url"], sha=hashlib.sha256(b).hexdigest(), units=units, assent=assent,
                          gazette=meta.get("gazette"), inf=inf, basis=basis,
                          folder=f"acts/{year}/{num}-{slug_of(c['title'])}"))
    items.sort(key=lambda x: (x["inf"], x["num"]))
    held_p.write_text(json.dumps(held, indent=1, ensure_ascii=False, sort_keys=True), "utf8")
    if dry:
        for it in items:
            print(it["inf"], it["folder"], len(it["units"]))
        print(len(items), "ready;", len(held), "held")
        return
    n = 0
    out = subprocess.run(["git", "-C", repo, "log", "--format=%at", "--max-count=2000"], capture_output=True, text=True)
    pre1970 = [max([int(x) for x in out.stdout.split() if x.isdigit() and int(x) < 86400] + [1000])]
    for it in items:
        d = Path(repo) / it["folder"]
        if d.exists():
            continue
        d.mkdir(parents=True)
        for k, u in it["units"].items():
            (d / f"{k}.md").write_bytes(u["text"].encode("utf8"))
        rows = "\n".join(f"| {u['title']} | [{k}.md]({k}.md) |" for k, u in sorted(it["units"].items()))
        (d / "README.md").write_bytes((f"# {it['title']}\n\n{it['short']} · as passed · in force {it['inf']} · "
                                       f"<https://repository.parliament.gh/handle/{it['handle']}>\n\n"
                                       f"| Provision | File |\n| --- | --- |\n{rows}\n").encode("utf8"))
        msg = (f"{it['short']} as enacted (Act {it['num']})\n\n"
               f"{it['title']}: the text as passed, from the text layer of the Parliament of Ghana Library's\n"
               f"edition (repository.parliament.gh). No OCR.\n\n"
               f"Law: Act {it['num']}\nKind: law\n"
               + (f"Enacted: {it['assent']}\n" if it["assent"] else "")
               + (f"Published: {it['gazette']}\n" if it["gazette"] else "")
               + f"In-force: {it['inf']}\nIn-force-basis: {it['basis']}\n"
               f"Source: https://repository.parliament.gh/handle/{it['handle']}\nSource-file: {it['url']}\n"
               f"Source-sha256: {it['sha']}\nText-source: publisher text layer\nAct: {it['short']}\n"
               f"Provisions: {len(it['units'])}\n")
        date = f"{it['inf']}T12:00:00+0000"
        if it["inf"] < "1970-01-02":
            pre1970[0] += 1
            date = f"@{pre1970[0]} +0000"
            msg = msg.replace("\n\nLaw: ", "\n\nGit cannot store a date before 1970, so this commit is dated 1 January 1970, "
                              "a second after the one\nbefore it. The day the change took effect is in the In-force "
                              "trailer, which tools/on.py reads.\n\nLaw: ", 1)
        env = dict(os.environ, GIT_AUTHOR_NAME=f"Act {it['num']}",
                   GIT_AUTHOR_EMAIL=f"act-{it['num']}@repository.parliament.gh.invalid",
                   GIT_COMMITTER_NAME="Lexifina", GIT_COMMITTER_EMAIL="ghana-law@lexifina.com",
                   GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
        subprocess.run(["git", "-C", repo, "add", "--", it["folder"]], check=True)
        r = subprocess.run(["git", "-C", repo, "commit", "-q", "-F", "-"], input=msg.encode(), env=env,
                           capture_output=True)
        if r.returncode:
            subprocess.run(["git", "-C", repo, "reset", "-q"], check=True)
            import shutil
            shutil.rmtree(d)
            log(f"commit failed Act {it['num']}: {r.stderr.decode()[:200]}")
            raise SystemExit(2)
        n += 1
        log(f"commit Act {it['num']} {it['folder']} {it['inf']}")
        if limit and n >= limit:
            break
    log(f"build: {n} committed, {len(held)} held")
    print(n, "committed;", len(held), "held")


if __name__ == "__main__":
    lim = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 0
    build(sys.argv[1], "--dry" in sys.argv, lim)
