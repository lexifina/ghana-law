"""Find Act PDFs hosted by Ghana government agencies (WordPress media search). One request in flight per host,
>=1.2 s apart; hosts run in parallel (<=8). Writes sec/cache/gov_media.jsonl (host, title, url)."""
import os
import json, re, sys, threading, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
UA = {"User-Agent": "Mozilla/5.0 (compatible; LexifinaLawArchive/1.0; +https://lexifina.com)"}
OUT = Path(os.path.join(os.environ.get("GH_ACQ", "."), 'sec/cache/gov_media.jsonl'))
HOSTS = """bog.gov.gh sec.gov.gh nca.org.gh epa.gov.gh mofep.gov.gh nic.gov.gh npra.gov.gh energycom.gov.gh purc.com.gh
mincom.gov.gh petrocom.gov.gh ppa.gov.gh lc.gov.gh gra.gov.gh fdaghana.gov.gh osp.gov.gh chraj.gov.gh ec.gov.gh
melr.gov.gh mojagd.gov.gh dataprotection.org.gh csa.gov.gh orc.gov.gh nlcghana.org fcghana.org gipc.gov.gh
moh.gov.gh moe.gov.gh mint.gov.gh mlnr.gov.gh nppa.gov.gh gsa.gov.gh gaca.gov.gh mesti.gov.gh gnfs.gov.gh
police.gov.gh nacoc.gov.gh eocoghana.org fic.gov.gh nia.gov.gh nhis.gov.gh gcaa.com.gh ghanaports.gov.gh
cocobod.gh gepaghana.org ncce.org.gh ncs.gov.gh audit.gov.gh cagd.gov.gh nca.gov.gh nab.gov.gh gtec.edu.gh
ges.gov.gh nacca.gov.gh ndpc.gov.gh nla.com.gh ghanalegal.gov.gh lawsghana.gov.gh mfa.gov.gh mint.gov.gh
statsghana.gov.gh nbssi.gov.gh gea.gov.gh fwsc.gov.gh ohcs.gov.gh psc.gov.gh lgs.gov.gh mlgdra.gov.gh
dvla.gov.gh nrsa.gov.gh gsb.gov.gh ghanastandards.gov.gh nmc.gov.gh mdcghana.org pharmacycouncil.org
gmc.gov.gh ghanamedicalcouncil.org nmcgh.org hefra.gov.gh nadmo.gov.gh gis.gov.gh immigration.gov.gh
prisons.gov.gh gaf.mil.gh nsb.gov.gh cybersecurity.gov.gh moc.gov.gh ncs.gov.gh ati.gov.gh boost.gov.gh
eximbankghana.com gnpc.com gridcogh.com vra.com ecg.com.gh bpa.gov.gh gmet.gov.gh wrc-gh.org fcwater.gov.gh
cwsa.gov.gh tcpa.gov.gh lands.gov.gh ghanalandsgateway.gov.gh rentcontrol.gov.gh nhia.gov.gh ghs.gov.gh
copyright.gov.gh rgd.gov.gh ipo.gov.gh jsghana.org judicial.gov.gh lrc.gov.gh lawreform.gov.gh""".split()
lock = threading.Lock()


def get(u):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40)
    return r.status, r.read()


def host(h):
    found = 0
    for base in (f"https://{h}", f"https://www.{h}"):
        try:
            st, b = get(f"{base}/wp-json/wp/v2/media?search=act&per_page=100&page=1&mime_type=application/pdf")
            items = json.loads(b)
        except Exception as e:
            time.sleep(1.2)
            continue
        page = 1
        while True:
            for it in items:
                rec = dict(host=h, base=base, title=re.sub(r"<[^>]+>", "", it.get("title", {}).get("rendered", "")),
                           url=it.get("source_url"), date=it.get("date"))
                with lock:
                    OUT.open("a", encoding="utf8").write(json.dumps(rec) + "\n")
                found += 1
            if len(items) < 100 or page >= 10:
                break
            page += 1
            time.sleep(1.2)
            try:
                st, b = get(f"{base}/wp-json/wp/v2/media?search=act&per_page=100&page={page}&mime_type=application/pdf")
                items = json.loads(b)
            except Exception:
                break
        print(h, base, found, flush=True)
        return
    print(h, "no wp media", flush=True)


with ThreadPoolExecutor(8) as ex:
    list(ex.map(host, sorted(set(HOSTS))))
