import os
import json, re, sys
import pymupdf
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "sec"))
import marg_read as M
ROOT = os.environ.get("GH_ACQ", ".")
rows = []
for x in json.load(open(ROOT + "/sec/scan_marg.json", encoding="utf8")):
    if not x["ok"]:
        continue
    f = f"{ROOT}/cache/pdf/{x['uuid']}.pdf"
    d = pymupdf.open(f)
    t = "\n".join(p.get_text() for p in d)
    imgs = sum(len(p.get_images()) for p in d)
    nums = re.findall(r"^Act\s*(\d{3,4})\s*$", t, re.M)
    ent = re.search(r"ENTITLED\s*\n(.*?)\n(?:AN\s+ACT|AN\s+ACI)", t, re.S)
    title = re.sub(r"\s+", " ", ent.group(1)).strip() if ent else None
    if not title:
        m = re.search(r"^([A-Z][A-Z ,()'.\-]{8,}(?:INSTRUMENT|RULES|REGULATIONS|ORDER)[A-Z ,()'.\-0-9]*)$", t, re.M)
        title = m.group(1).strip() if m else None
    ei = re.search(r"\b(E|L|C)\.\s?I\.?\s*(\d{1,4})\b", t[:600])
    u, e, meta = M.read(f, x["kind"])
    x.update(title=title, actnum=max(set(nums), key=nums.count) if nums else None, imgs=imgs,
             producer=d.metadata.get("producer"), inst=(ei.group(1) + ".I. " + ei.group(2)) if ei else None)
    rows.append(x)
    print(x["kind"][:4], x["actnum"], x["inst"], x["assent"], x["gazette"], x["made"], imgs, (x["producer"] or "")[:25], "|", title, "|", x["name"][:50])
json.dump(rows, open(ROOT + "/sec/marg_info.json", "w", encoding="utf8"), indent=1)
