"""Download legislation-looking PDFs from gov_media.jsonl (one per host at a time, 1.2 s apart) and triage them:
Act number and title from the masthead, whether the repo has it, and which reader reads it.
Writes sec/gov_triage.json."""
import os
import hashlib, json, re, sys, threading, time, urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "sec"))
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "tools"))
import build as B, marg_read as M, wipo_read as W
import pymupdf
UA = {"User-Agent": "Mozilla/5.0 (compatible; LexifinaLawArchive/1.0; +https://lexifina.com)"}
C = Path(os.path.join(os.environ.get("GH_ACQ", "."), 'sec/cache/gov'))
REPO = Path(os.path.join(os.environ.get("GH_ACQ", "."), 'repo'))
have = {int(re.match(r"(\d+)-", p.name).group(1)) for p in REPO.glob("acts/*/*") if re.match(r"\d+-", p.name)}
SKIP = re.compile(r"practice|note|news|faq|speech|address|press|statement|manual|brochure|profile|plan|report|"
                  r"guideline|regulation|form|questionnaire|literacy|impact|key-changes|abridged|demo|eoi|"
                  r"expression|standard|policy|bill|directive|notice|sensiti|workshop|launch|igaps", re.I)
recs, seen = [], set()
for l in open(C.parent / "gov_media.jsonl", encoding="utf8"):
    r = json.loads(l)
    t = r["title"] + " " + r["url"].rsplit("/", 1)[-1]
    if r["url"] in seen or SKIP.search(t) or not re.search(r"\bact|law|decree|code", t, re.I):
        continue
    seen.add(r["url"])
    recs.append(r)
by_host = defaultdict(list)
for r in recs:
    by_host[r["host"]].append(r)
print(len(recs), "candidates on", len(by_host), "hosts", flush=True)


def fetch_host(rs):
    for r in rs:
        f = C / r["host"] / urllib.request.unquote(r["url"].rsplit("/", 1)[1])
        r["file"] = str(f)
        if f.exists():
            continue
        f.parent.mkdir(parents=True, exist_ok=True)
        try:
            f.write_bytes(urllib.request.urlopen(urllib.request.Request(r["url"], headers=UA), timeout=120).read())
        except Exception as e:
            r["err"] = str(e)[:80]
        time.sleep(1.2)


with ThreadPoolExecutor(6) as ex:
    list(ex.map(fetch_host, by_host.values()))

out = []
for r in recs:
    f = Path(r["file"])
    if not f.exists():
        out.append(r | {"verdict": "fetch failed"}); continue
    try:
        d = pymupdf.open(f)
        txt = "\n".join(p.get_text() for p in d)
    except Exception as e:
        out.append(r | {"verdict": f"bad pdf {e}"[:60]}); continue
    r["sha256"] = hashlib.sha256(f.read_bytes()).hexdigest()
    r["pages"] = d.page_count
    r["dens"] = len(txt) // max(1, d.page_count)
    head = " ".join(txt[:6000].split())
    m = re.search(r"\bACT\s+(\d{1,4})\b(?!\s*of)", head)
    r["num"] = int(m.group(1)) if m else None
    r["amended"] = bool(re.search(r"As amended by|consolidat", head, re.I))
    r["in_repo"] = r["num"] in have
    res = {}
    if r["dens"] >= 150:
        for name, fn in (("build", lambda: B.read(f.read_bytes())), ("marg", lambda: M.read(str(f), "act")),
                         ("wipo", lambda: W.read(str(f)))):
            try:
                u, e, meta = fn()
            except Exception as ex:
                u, e, meta = None, f"EXC {ex}", {}
            res[name] = [bool(u), (e or "")[:70], meta.get("assent"), meta.get("gazette"), meta.get("sections"),
                         len(u or {})]
    r["res"] = res
    r["ok"] = [k for k, v in res.items() if v[0]]
    out.append(r)
    print(r["num"], "REPO" if r["in_repo"] else "new ", "AMD" if r["amended"] else "   ", r["dens"], r["ok"],
          {k: v[2] for k, v in res.items() if v[2]}, "|", r["host"], r["title"][:60], flush=True)
json.dump(out, open(C.parent.parent / "gov_triage.json", "w", encoding="utf8"), indent=1)
