"""Reader for Acts of Parliament of Ghana printed by the Assembly Press (Ghana Publishing Company), text layer only.

The print: a bold section heading above each section; the section starts "N. (1) ..." with the number in bold;
group headings ("Cyber Security Authority", "Miscellaneous Provisions") are short italic lines, centred; the
enacted text runs from "PASSED by Parliament and assented to by the President" to the printer's colophon
("PRINTED BY ..."/"Date of Gazette notification"); schedules start with a centred "FIRST SCHEDULE" etc.
Running heads (title, "Act N", page number) are outside the body band and are dropped.

read(pdf_path, cfg) -> (units, report). Deterministic; no OCR. The report carries a word-for-word fidelity check:
every word of the enacted text as printed is in a provision file or in a dropped group heading, and none is added.
"""
from __future__ import annotations

import collections
import re

QUOTES = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'", " ": " ", "–": "-",
                        "—": "—", "…": "..."})
ENUM = re.compile(r"^\((?:[a-z]{1,3}|[ivxl]{1,6}|\d{1,3}[A-Za-z]?)\)(?=\s|$)")
SEC = re.compile(r"^(\d{1,3}[A-Z]?)\.\s+(?=\S)|^(\d{1,3}[A-Z]?)\.$")
SCHED = re.compile(r"^(FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH|ELEVENTH|TWELFTH)?\s*SCHEDULE$")


def norm(s: str) -> str:
    s = s.translate(QUOTES)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r" ([;:,])", r"\1", s)
    return s


class Line:
    __slots__ = ("page", "x0", "y0", "x1", "text", "bold", "italic", "lead_bold", "pieces")

    def __init__(self, page, x0, y0, x1, text, bold, italic, lead_bold, pieces=None):
        self.page, self.x0, self.y0, self.x1, self.text = page, x0, y0, x1, text
        self.bold, self.italic, self.lead_bold = bold, italic, lead_bold
        self.pieces = pieces or [(x0, text)]


def lines_of(doc, first: int, last: int, top: float, bottom: float) -> list[Line]:
    out: list[Line] = []
    for i in range(first, last + 1):
        page_lines = []
        for b in doc[i].get_text("rawdict")["blocks"]:
            if b.get("type") != 0:
                continue
            for ln in b["lines"]:
                for s in ln["spans"]:
                    s["text"] = "".join(c["c"] for c in s["chars"])
                spans = [s for s in ln["spans"] if s["text"].strip()]
                if not spans:
                    continue
                y0 = min(s["bbox"][1] for s in spans)
                y1 = max(s["bbox"][3] for s in spans)
                if y0 < top or y0 >= bottom:
                    continue
                page_lines.append([min(s["bbox"][0] for s in spans), y0, max(s["bbox"][2] for s in spans), spans])
        # pieces of one printed line (same baseline) are joined left to right
        page_lines.sort(key=lambda r: (round(r[1]), r[0]))
        merged: list[list] = []
        for x0, y0, x1, spans in page_lines:
            if merged and abs(merged[-1][1] - y0) < 3:
                merged[-1][2] = max(merged[-1][2], x1)
                merged[-1][3] = merged[-1][3] + spans
                merged[-1][0] = min(merged[-1][0], x0)
            else:
                merged.append([x0, y0, x1, list(spans)])
        for x0, y0, x1, spans in merged:
            spans = sorted(spans, key=lambda s: s["bbox"][0])
            txt = ""
            for k, s in enumerate(spans):
                if k and not txt.endswith(" ") and not s["text"].startswith(" ") \
                        and s["bbox"][0] - spans[k - 1]["bbox"][2] > 1.0:
                    txt += " "
                txt += s["text"]
            # runs of text separated by a wide gap (table cells), from the characters' own positions
            # (a span's own text is kept as it is; a span is cut only at a run of three or more spaces or at a gap of
            # more than 12 points between two characters, and spans more than 12 points apart are separate pieces)
            pieces: list[list] = []
            last_x1 = None
            for s in spans:
                run_spaces = 0
                for c in s["chars"]:
                    if not c["c"].strip():
                        run_spaces += 1
                        if pieces:
                            pieces[-1][1] += " "
                        continue
                    if last_x1 is None or c["bbox"][0] - last_x1 > 12.0 or run_spaces >= 3:
                        pieces.append([c["bbox"][0], ""])
                    elif c is s["chars"][0] and c["bbox"][0] - last_x1 > 1.0 and not pieces[-1][1].endswith(" "):
                        pieces[-1][1] += " "
                    run_spaces = 0
                    pieces[-1][1] += c["c"]
                    last_x1 = max(c["bbox"][2], c["bbox"][0])
            bold = all(s["flags"] & 16 for s in spans)
            italic = all(s["flags"] & 2 for s in spans)
            out.append(Line(i, x0, y0, x1, norm(txt), bold, italic, bool(spans[0]["flags"] & 16),
                            [(px, norm(pt)) for px, pt in pieces if norm(pt)]))
    return [l for l in out if l.text]


def paragraphs(lines: list[Line], right: dict[int, float]) -> list[str]:
    """One paragraph per line of output: a line starts a paragraph if it starts with an enumerator, if the line before
    it ends short of the right margin (the last line of a justified paragraph), or by a first-line indent."""
    paras: list[str] = []
    prev = None
    for l in lines:
        t = l.text
        new = prev is None or ENUM.match(t) or prev.x1 < right[prev.page] - 25 or (
            prev.page == l.page and l.x0 > prev.x0 + 6 and re.search(r"[;:.]$|\b(?:and|or)$", prev.text)
            and not re.match(r"[a-z]", t)) or (
            prev.page != l.page and re.search(r"[;:.]$", prev.text) and re.match(r'[A-Z"(]', t)
            and l.x0 > _left(lines, l.page) + 6)
        if new:
            paras.append(t)
        else:
            # a line-end hyphen in a word broken across lines is kept as printed: "re-" + "registration"
            paras[-1] += ("" if paras[-1].endswith("-") and re.match(r"[a-z]", t) else " ") + t
        prev = l
    return paras


def _left(lines: list[Line], page: int) -> float:
    xs = [l.x0 for l in lines if l.page == page]
    return min(xs) if xs else 0.0


class Unit:
    def __init__(self, key, label, kind, heading):
        self.key, self.label, self.kind, self.heading, self.lines = key, label, kind, heading, []
        self.table = None


TABLE_HEAD = re.compile(r"^Column 1(?!\d)")


def table_rows(lines: list[Line], cols: list[float]) -> list[str]:
    """A table printed in columns ("Column 1 Column 2 ..."): each piece of text goes to the column it starts in; a row
    starts with a piece in the first column (or on a new page); a row is one output line, cells joined by " | "."""
    rows: list[list[list[str]]] = []
    for l in lines:
        for px, pt in l.pieces:
            c = max(k for k in range(len(cols)) if k == 0 or px >= cols[k] - 15)
            if c == 0 and (not rows or any(rows[-1][1:]) or not rows[-1][0]):
                rows.append([[] for _ in cols])
            elif not rows:
                rows.append([[] for _ in cols])
            rows[-1][c].append(pt)
    return [" | ".join(" ".join(cell) for cell in r) for r in rows]


def read(doc, cfg: dict) -> tuple[dict, dict]:
    first, last = cfg["pages"]
    last = len(doc) - 1 if last is None else last
    seq = lines_of(doc, first, last, cfg["top"], cfg["bottom"])
    start = re.compile(cfg.get("start", r"^PASSED by Parliament"))
    stop = re.compile(cfg.get("stop", r"^PRINTED BY|^Date of Gazette notification"))
    i0 = next(k for k, l in enumerate(seq) if start.search(l.text))
    seq = seq[i0 + 1:]
    k = next((k for k, l in enumerate(seq) if stop.search(l.text)), None)
    if k is not None:
        seq = seq[:k]
    words = [w for l in seq for w in re.findall(r"\w+", l.text)]
    right: dict[int, float] = {}
    for l in seq:
        right[l.page] = max(right.get(l.page, 0.0), l.x1)
    units: list[Unit] = []
    report = {"structure_lines": [], "no_heading": [], "orphans": [], "out_of_sequence": []}
    pending_head: list[str] = []
    cur: Unit | None = None
    prev_num = 0
    in_sched = False
    sch_n = 0
    for idx, l in enumerate(seq):
        t = l.text
        if SCHED.match(t) and prev_num:
            in_sched = True
            sch_n += 1
            cur = Unit(f"sch-{sch_n:02d}", t.title(), "schedule", t)
            units.append(cur)
            continue
        if in_sched:
            if TABLE_HEAD.match(t) and len(l.pieces) >= 2:
                cur.table = [px for px, _ in l.pieces]
                cur.lines.append(l)
                continue
            cur.lines.append(l)
            continue
        m = SEC.match(t)
        if m and l.lead_bold:
            num = m.group(1) or m.group(2)
            n = int(re.match(r"\d+", num).group(0))
            if n != prev_num + 1 and not (n == prev_num and re.search(r"[A-Z]$", num)):
                report["out_of_sequence"].append(num)
            prev_num = n
            head = " ".join(pending_head) if pending_head else None
            pending_head = []
            if head is None:
                report["no_heading"].append(num)
            cur = Unit(f"sec-{n:03d}" + (f"-{num[-1].lower()}" if re.search(r"[A-Z]$", num) else ""),
                       f"Section {num}", "sec", head)
            rest = t[m.end():].strip()
            if rest:
                cur.lines.append(Line(l.page, l.x0, l.y0, l.x1, rest, False, False, False))
            units.append(cur)
            continue
        if l.bold:
            pending_head.append(t)
            continue
        if l.italic and not ENUM.match(t) and not re.search(r"[;:,]$", t):
            # a group heading (italic, centred): left out of every unit, listed
            report["structure_lines"].append(t)
            continue
        if cur is None:
            report["orphans"].append(t)
            continue
        if pending_head:  # bold text inside a section that is not a heading: keep it as body
            for h in pending_head:
                cur.lines.append(Line(l.page, l.x0, l.y0, l.x1, h, False, False, False))
            pending_head = []
        cur.lines.append(l)
    if pending_head:
        report["orphans"] += pending_head
    out = {}
    for u in units:
        if u.table is not None:
            # a table: from its "Column 1 ..." heading on, each printed line is one line of the file, its cells (runs
            # of text separated by a wide gap) joined by " | ", in print order (rows are not reassembled)
            k = next(i for i, l in enumerate(u.lines) if TABLE_HEAD.match(l.text))
            body = paragraphs(u.lines[:k], right) + [" | ".join(pt for _, pt in l.pieces) for l in u.lines[k:]]
        else:
            body = paragraphs(u.lines, right)
        if u.kind == "sec":
            num = u.label.split()[-1]
            head = f"# {num}. {u.heading.rstrip('.')}" if u.heading else f"# {u.label}"
        else:
            head = f"# {u.heading}"
        out[u.key] = {"label": u.label, "kind": u.kind, "text": "\n".join([head] + body) + "\n"}
    # fidelity: every printed word is in a unit (heading line included: section headings are printed text) or in a
    # dropped group heading, and nothing is added
    printed = collections.Counter(words)
    ours = collections.Counter()
    for uu in out.values():
        ours.update(re.findall(r"\w+", uu["text"].replace("# ", "", 1)))
    for t in report["structure_lines"] + report["orphans"]:
        ours.update(re.findall(r"\w+", t))
    report.update({"units": len(out), "sections": sum(1 for k in out if k.startswith("sec-")),
                   "schedules": [k for k in out if k.startswith("sch-")],
                   "words_printed": sum(printed.values()), "words_kept": sum(ours.values()),
                   "words_missing": sorted((printed - ours).items()), "words_added": sorted((ours - printed).items())})
    return out, report
