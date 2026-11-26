"""Reader for Ghanaian Acts/Instruments printed with marginal notes ("Title" line, then "N. text").

read(path) -> (units, err, meta). Text layer only (no OCR of ours). Body: from "PASSED by Parliament" /
"BE IT ENACTED" / the enabling words ("IN exercise of ...") to "Date of Gazette notification" / "PRINTED BY".
A line "N. ..." (or "N." alone) starts provision N only when N is the next number (or a lettered insert).
The marginal note is the one line above it with no closing punctuation; other such lines directly above
(group and Part headings) and running heads (the title, "Act N", page numbers) are left out and counted.
Checks: provisions 1..N without a gap; equal to the Arrangement where printed; every word of the body is in a
provision file or in a counted left-out line.
"""
import os
import collections, re, sys
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "tools"))
import build as B  # noqa

NUM = re.compile(r"^(\d{1,3})([A-Z]?)\.(?:\s+(.*))?$")
SCHED = re.compile(r"^((FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH)\s+)?SCHEDULES?\b.*$")


def raw_lines(path):
    import pymupdf
    d = pymupdf.open(path)
    L = []
    for p in d:
        for s in p.get_text().split("\n"):
            s = re.sub(r"\s+", " ", s.replace("\u00a0", " ").replace("\u00ad", "")).strip()
            if s:
                L.append(s)
    return L, d.page_count


def read(path, kind="act"):
    L, pages = raw_lines(path)
    joined = "\n".join(L)
    meta = {"pages": pages}
    if len(joined) < 300 * pages * 0.5:
        return None, "image-only PDF (no text layer)", meta
    m = re.search(r"DATE\s+OF\s+AS\s?SENT\s*:?\s*([^\n]{6,40})", joined, re.I)
    meta["assent"] = B.day(m.group(1)) if m else None
    m = re.search(r"Gazette\s+[Nn]otification\s*:?\s*([^\n]{6,40})", joined)
    meta["gazette"] = B.day(m.group(1)) if m else None
    m = re.search(r"made\s+this\s+(\d{1,2}\w*\s+day\s+of\s+\w+,?\s*\d{4})", joined.replace("\n", " "), re.I)
    meta["made"] = B.day(m.group(1)) if m else None
    start = next((i for i, s in enumerate(L) if re.match(r"^(PASSED\s+by\s+Parliament|BE\s+IT\s+ENACTED)", s, re.I)), None)
    if start is None:
        start = next((i for i, s in enumerate(L) if re.match(r"^IN\s+exercise\s+of", s, re.I)), None)
        if start is None:
            return None, "no enacting words", meta
        k = start
        while k < len(L) and not re.search(r"\d{4}\s*\.?$", L[k]):
            k += 1
        pre = L[start:k + 1]
        start = k
    else:
        p0 = next((k for k in range(start, -1, -1) if re.match(r"^AN\s+ACT\b", L[k])), start)
        pre = L[p0:start + 1]
    end = next((i for i in range(start + 1, len(L)) if re.match(r"^(Date\s+of\s+Gazette|PRINTED\s+BY)", L[i], re.I)), len(L))
    body = L[start + 1:end]
    # running heads: the title as printed on top of pages, "Act N", bare numbers
    title_lines = set()
    for s in L[:start]:
        if re.search(r"\b(ACT|INSTRUMENT|REGULATIONS|RULES|ORDER),?\s*\d{4}", s, re.I) and len(s) < 120:
            title_lines.add(s.lower().replace(" ", ""))
    run = lambda s: (re.fullmatch(r"\d{1,3}|[A-Z]|Act\s*\d{1,4}|(E|L|C)\.\s?I\.?\s*\d+|REPUBLIC OF GHANA", s)
                     or s.lower().replace(" ", "") in title_lines)
    dropped, B_ = [], []
    for s in body:
        (dropped if run(s) else B_).append(s)
    body = B_
    heads, prev = [], (0, "")
    sched_line = next((i for i, s in enumerate(body) if SCHED.match(s) and s.upper() == s), len(body))
    for i, s in enumerate(body[:sched_line]):
        m = NUM.match(s)
        if not m:
            continue
        n, let = int(m.group(1)), m.group(2)
        if (not let and n == prev[0] + 1) or (let and n == prev[0] and let > prev[1]):
            heads.append((i, n, let))
            prev = (n, let)
    if not heads:
        return None, "no numbered provisions", meta
    # schedules: from the first all-caps SCHEDULE line after the last provision
    last = heads[-1][0]
    sch_at = next((i for i in range(last + 1, len(body)) if SCHED.match(body[i]) and body[i].upper() == body[i]), len(body))
    tail = body[sch_at:]
    body = body[:sch_at]
    units = {}
    label = "Section" if kind == "act" else "Paragraph"
    bounds = [h[0] for h in heads] + [len(body)]
    for k, (i, n, let) in enumerate(heads):
        seg = body[i:bounds[k + 1]]
        # lines at the end of this segment that belong above the next number: marginal note + headings
        title_next = []
        while k + 1 < len(heads) and seg and not re.search(r"[.;:,\u2014\-]$", seg[-1]) and not seg[-1].startswith("(") \
                and len(seg) > 1 and len(seg[-1]) < 90:
            title_next.insert(0, seg.pop())
        heads[k] = (i, n, let, title_next)
        units[(n, let)] = seg
    # marginal note of provision 1: lines above it in the body
    first = [s for s in body[:heads[0][0]]]
    notes = {}
    prevnotes = first
    for k, (i, n, let, tn) in enumerate(heads):
        idx = [q for q, s in enumerate(prevnotes) if not re.search(r"[.;:,]$", s) and not s.isupper()]
        if not idx:
            idx = [q for q, s in enumerate(prevnotes) if not re.search(r"[.;:,]$", s)]
        j = idx[-1] if idx else None
        notes[(n, let)] = prevnotes[j] if j is not None else ""
        dropped += [s for q, s in enumerate(prevnotes) if q != j]
        prevnotes = tn
    out = {}
    for (n, let), seg in units.items():
        m = NUM.match(seg[0])
        lines = ([m.group(3)] if m.group(3) else []) + seg[1:]
        out[f"sec-{n:03d}{let.lower()}"] = {"title": f"{label} {n}{let}",
                                             "text": f"# {n}{let}. {notes[(n, let)].rstrip('.')}\n" + B.paras(lines) + "\n"}
    out["preamble"] = {"title": "Preamble" if kind == "act" else "Enabling words", "text": B.paras(pre) + "\n"}
    sch, cur = [], None
    for s in tail:
        if SCHED.match(s) and s.upper() == s and (cur is None or len(cur) > 1):
            cur = [s]
            sch.append(cur)
        elif cur is not None:
            cur.append(s)
    for q, block in enumerate(sch, 1):
        out[f"schedule-{q:02d}"] = {"title": f"Schedule {q}", "text": f"# {block[0]}\n" + B.paras(block[1:]) + "\n"}
    plain = [h[1] for h in heads if not h[2]]
    meta["sections"], meta["last"] = len(heads), plain[-1]
    # arrangement
    a0 = next((i for i, s in enumerate(L[:start]) if re.match(r"ARRANGEMENT\s+OF", s, re.I)), None)
    if a0 is not None:
        arr = re.findall(r"^(\d{1,3}[A-Z]?)\s*[.,]", "\n".join(L[a0:start]), re.M)
        got = [f"{h[1]}{h[2]}" for h in heads]
        meta["arrangement"] = len(set(arr))
        if set(arr) != set(got):
            return None, f"arrangement {len(set(arr))} vs read {len(got)}: missing {sorted(set(arr) - set(got), key=lambda x: (len(x), x))[:8]}", meta
    src = collections.Counter(re.findall(r"\w+", "\n".join(L[start + 1:end])))
    kept = collections.Counter(re.findall(r"\w+", " ".join(u["text"] for k, u in out.items() if k != "preamble")
                                          + " " + " ".join(dropped)))
    lost = src - kept
    meta["words"] = (sum(src.values()), sum(kept.values()))
    meta["dropped"] = dropped
    if lost:
        return None, f"word check: {sum(lost.values())} words not kept {list(lost.items())[:8]}", meta
    return out, None, meta


if __name__ == "__main__":
    u, e, m = read(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "act")
    print(e, {k: v for k, v in m.items() if k != "dropped"})
    print("dropped:", m.get("dropped", [])[:40])
    if u:
        ks = sorted(u)
        for k in ks[:3] + ks[-3:]:
            print("----", k, "\n" + u[k]["text"][:300])
