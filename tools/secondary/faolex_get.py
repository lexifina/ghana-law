"""Fetch FAOLEX PDFs only for ECOLEX records that are Acts not already in the repository (titles naming an Act
number we lack, or Acts/Decrees/Laws without a number). Policies, plans, regulations and instruments are skipped."""
import json, re, time, urllib.request
from pathlib import Path
UA = {"User-Agent": "Mozilla/5.0 (compatible; LexifinaLawArchive/1.0; +https://lexifina.com)"}
C = Path(r"%GH_ACQ%\sec\cache")
REPO = Path(r"%GH_ACQ%\repo")
have = {int(re.match(r"(\d+)-", p.name).group(1)) for p in REPO.glob("acts/*/*") if re.match(r"\d+-", p.name)}
recs = json.load(open(C / "ecolex/list.json", encoding="utf8"))
LOG = open(C / "ecolex" / "log.txt", "a", encoding="utf8", buffering=1)
want = []
for i, r in recs.items():
    t = r["title"]
    if re.search(r"\b(L\.?\s?I\.?|C\.?\s?I\.?|E\.?\s?I\.?)\s*\d+|Regulations|Rules|Polic|Plan\b|Strateg|Programme|Guideline|Framework|Order|Notice|Bye-?laws?|Instrument|Ghana at|Vision|Report|Manual|Charter|Agreement|Convention|Protocol|Memorandum", t, re.I):
        continue
    if not re.search(r"\b(Act|Decree|Law|Ordinance|Code)\b", t, re.I):
        continue
    m = re.search(r"\((?:Act|No\.?)\s*(\d{1,4})\)|Act,?\s*(?:No\.?\s*)?(\d{3,4})\b", t)
    num = int(m.group(1) or m.group(2)) if m else None
    if num and num in have:
        continue
    y = re.search(r"\b(19[5-9]\d|20[0-2]\d)\b", t)
    if not num or not y or int(y.group(1)) < 1993:
        continue
    want.append((i, t))
LOG.write(f"faolex want {len(want)}\n")
print(len(want))
import sys
if "--dry" in sys.argv:
    for i, t in want:
        print(i, t[:100])
    raise SystemExit
for i, t in want:
    f = C / "faolex" / f"gha{i}.pdf"
    if f.exists():
        continue
    for attempt in range(3):
        try:
            f.write_bytes(urllib.request.urlopen(urllib.request.Request(f"https://faolex.fao.org/docs/pdf/gha{i}.pdf", headers=UA), timeout=180).read())
            LOG.write(f"pdf {i} ok\n")
            break
        except Exception as e:
            LOG.write(f"pdf {i} {e}\n")
            time.sleep(10)
    time.sleep(1)
LOG.write("faolex done\n")
