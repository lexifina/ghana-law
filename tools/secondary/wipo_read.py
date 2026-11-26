"""Reader for WIPO Lex consolidations of Ghanaian Acts typed in Word ("Section Nâ€”Title" headings).

read(pdf_path) -> (units, err, meta). Sequence-guided: a "Section X" line is a heading only when X is the next
number (n+1) or a lettered insert after n (nA, nB ...). Lines a heading wraps onto are joined. Part/Chapter lines and
group headings directly above a heading are left out (counted). Everything after the last section is split into
Schedules at all-caps "... SCHEDULE" lines; amending-Act texts appended after the Code (all-caps "... ACT, YYYY (ACT N)"
titles) are cut off. Checks: sections 1..N without a gap, equal to the Arrangement of Sections; word check.
"""
import os
import re, sys
from pathlib import Path
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "tools"))
import build as B  # noqa

HEAD = re.compile(r"^Section\s+(\d{1,3})([A-Z]{0,2})\s*(?:[—–\-]+\s*(.*)|\.?\s*(.*))$")
GROUP = re.compile(r"^(PART|CHAPTER|SUB-PART)\b")
AMEND_TITLE = re.compile(r"^[A-Z0-9 ,()'’\-—.]+\bACT,?\s*\d{4}\s*\(ACT\s*\d+\)?\.?$")


def lines(path):
    import pymupdf
    d = pymupdf.open(path)
    L = []
    for p in d:
        for s in p.get_text().split("\n"):
            s = s.replace("\u00a0", " ").strip()
            if re.fullmatch(r"\d{1,3}", s):
                continue
            L.append(s)
    # join a "Section" heading broken one word per line
    out, i = [], 0
    while i < len(L):
        if L[i] == "Section" and i + 1 < len(L) and re.match(r"^\d{1,3}[A-Z]?\s*[—–\-]", L[i + 1]):
            j, parts = i + 1, ["Section"]
            while j < len(L) and len(parts) < 40:
                parts.append(L[j])
                j += 1
                if parts[-1].endswith("."):
                    break
            out.append(" ".join(parts))
            i = j
            continue
        out.append(L[i])
        i += 1
    return [s for s in out if s]


def succ(prev, n, let):
    pn, pl = prev
    if let:
        return n == pn and (pl < let) or (n == pn + 1 and False)
    return n == pn + 1


def read(path):
    L = lines(path)
    joined = "\n".join(L)
    meta = {}
    m = re.search(r"DATE\s+OF\s+ASSENT\s*:?\s*([^\n]{6,60})", joined, re.I)
    meta["assent"] = B.day(m.group(1)) if m else None
    # arrangement
    a0 = next((i for i, s in enumerate(L) if re.match(r"ARRANGEMENT\s+OF\s+SECTIONS", s, re.I)), None)
    heads, prev, i = [], (0, ""), 0
    first_body = None
    for i, s in enumerate(L):
        m = HEAD.match(s)
        if not m:
            continue
        n, let = int(m.group(1)), m.group(2)
        ok = (not let and n == prev[0] + 1) or (let and n == prev[0] and let > prev[1])
        if not ok:
            continue
        heads.append((i, n, let, (m.group(3) or m.group(4) or "").strip()))
        prev = (n, let)
    if not heads:
        return None, "no Section headings", meta
    arr_nums = None
    if a0 is not None:
        arr_txt = "\n".join(L[a0:heads[0][0]])
        arr_nums = set(re.findall(r"^(\d{1,3}[A-Z]?)\.\s", arr_txt, re.M))
    units, dropped = {}, 0
    first = heads[0][0]
    p0 = next((k for k in range(first - 1, -1, -1) if re.match(r"^AN\s+ACT\b", L[k])), None)
    if p0 is None:
        p0 = next((k for k in range(first - 1, -1, -1) if re.match(r"^DATE\s+OF\s+ASSENT", L[k], re.I)), None)
    tail = []
    for k, (i, n, let, ttl) in enumerate(heads):
        j = heads[k + 1][0] if k + 1 < len(heads) else len(L)
        body = L[i + 1:j]
        # a heading that wraps: continuation lines until one ends with "." (title lines end with ".")
        while ttl and not ttl.endswith(".") and body and len(body[0]) < 90 and not re.match(r"^\(\d|^\(\w\)", body[0]) \
                and (body[0][:1].isupper() or body[0].startswith("Section")) and len(ttl) < 160:
            ttl = ttl + " " + body.pop(0)
        if k + 1 == len(heads):
            for q, s in enumerate(body):
                if (re.search(r"\bSCHEDULE\b", s) and s.upper() == s) or AMEND_TITLE.match(s) or s == "FOOTNOTES" or (len(s) > 15 and s.upper() == s and re.search(r"\bACT\b", s)):
                    tail, body = body[q:], body[:q]
                    break
        # drop Part/Chapter lines and group headings at the end of the body (they belong to the next heading)
        DROPPED_LINES = meta.setdefault("dropped_lines", [])
        while body and (GROUP.match(body[-1]) or (not re.search(r"[.;:,—\-]$", body[-1]) and len(body) > 1
                                                    and re.search(r"[.;:]$", body[-2]) and len(body[-1]) < 80
                                                    and body[-1][:1].isupper() and not re.search(r"[0-9¢]", body[-1]))):
            DROPPED_LINES.append(body.pop())
            dropped += 1
        key = f"sec-{n:03d}" + let.lower()
        units[key] = {"title": f"Section {n}{let}", "text": f"# {n}{let}. {ttl.rstrip('.')}\n" + B.paras(body) + "\n"}
    if p0 is not None:
        pre = [s for s in L[p0:first] if not GROUP.match(s)]
        units["preamble"] = {"title": "Preamble", "text": B.paras(pre)}
    sch, cur = [], None
    for s in tail:
        if AMEND_TITLE.match(s) or s == "FOOTNOTES" or (len(s) > 15 and s.upper() == s and re.search(r"\bACT\b", s) and not re.search(r"\bSCHEDULE\b", s)):
            break
        if re.search(r"\bSCHEDULE\b", s) and s.upper() == s and (cur is None or len(cur) > 1):
            cur = [s]
            sch.append(cur)
        elif cur is not None:
            cur.append(s)
    for q, block in enumerate(sch, 1):
        units[f"schedule-{q:02d}"] = {"title": f"Schedule {q}", "text": f"# {block[0]}\n" + B.paras(block[1:]) + "\n"}
    plain = [h[1] for h in heads if not h[2]]
    meta["sections"] = len(heads)
    meta["last"] = plain[-1]
    if plain != list(range(1, len(plain) + 1)):
        return None, "sections not 1..N", meta
    got = {f"{h[1]}{h[2]}" for h in heads}
    if arr_nums is not None:
        miss, extra = sorted(arr_nums - got), sorted(got - arr_nums)
        meta["arrangement_missing"], meta["arrangement_extra"] = miss, extra
    # word check over the body from the first heading to the end of the sections and schedules
    import collections
    used_tail = sum(sch, [])
    end = heads[-1][0] + 1 + (len(L) - heads[-1][0] - 1)
    span = L[first:len(L) - len(tail)] + used_tail
    src = collections.Counter(re.findall(r"\w+", "\n".join(span)))
    src["Section"] -= len(heads)
    kept = collections.Counter(re.findall(r"\w+", " ".join(u["text"] for k, u in units.items() if k != "preamble")
                                          + " " + " ".join(meta.get("dropped_lines", []))))
    lost = src - kept
    meta["words"] = (sum(src.values()), sum(kept.values()), dropped)
    meta["lost"] = sum(lost.values())
    meta["dropped_sample"] = meta.get("dropped_lines", [])[:50]
    if lost:
        return None, f"word check: {sum(lost.values())} words not kept {list(lost.items())[:10]}", meta
    return units, None, meta


if __name__ == "__main__":
    u, e, m = read(sys.argv[1])
    print(e, {k: v for k, v in m.items()})
    if u:
        print(len(u), "units")
        for k in list(u)[:3] + list(u)[-4:]:
            print("----", k, "\n", u[k]["text"][:400])
