"""Parliament of Ghana Library repository (DSpace 7 REST API) fetcher.

    python -X utf8 tools/fetch.py            # catalogue every scope, then the ORIGINAL PDFs, scopes in order

Up to 4 requests in flight, >= 0.25 s between starts; back off on 429/5xx; stop on 403 or a challenge page.
Catalogue -> catalogue.jsonl (one item per line, with its ORIGINAL bitstreams). PDFs -> cache/pdf/<bitstream>.pdf.
Every request is logged to cache/requests.jsonl; progress to progress.log.
"""
import json, os, sys, threading, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "cache"
API = "https://repository.parliament.gh/server/api"
UA = "Mozilla/5.0 (compatible; LexifinaLawArchive/1.0; +https://lexifina.com)"
# (scope uuid, kind) in build order: Acts first, then decrees, then instruments
SCOPES = [
    ("fe201343-9105-4778-adb7-b0f0f8c09b7c", "act"), ("61560d33-906b-4040-ab6d-669b7e79a7db", "act"),
    ("8e2d2072-408d-4089-b4f8-8cc54f0ac31a", "act"), ("51b0be71-62ff-4b00-bcd3-38162321701f", "act"),
    ("4cfeb40f-5ebd-4796-bc68-bcd2ffcf82b2", "act"), ("7a749b67-495e-4848-b743-3fa130bc08e4", "act"),
    ("78448d72-f173-434f-a85b-1e82e57e5833", "act"), ("f8cd70d7-8905-4575-a19f-790896923c62", "act"),
    ("7d0cae9e-9e0c-468a-96a9-518ff9872429", "act"), ("a8ad0c36-4041-4ce1-9eaf-e464636e044e", "act"),
    ("f7f6e93f-d293-4ce2-b488-707859a3df09", "act"),
    ("f5d2bc97-2c45-4488-b885-1b6bfdfa5c59", "decree"), ("0294cb9b-e23d-45cf-beea-c769eec515f2", "decree"),
    ("d618dab7-37cb-43ef-b49e-d9e905e533c4", "decree"), ("4ec64c0a-04ff-44a6-b0da-d40b67a1223d", "decree"),
    ("a29e3b78-ce23-4115-b7c2-8fac3b9ddbf6", "decree"), ("b01346d2-b5df-429a-b698-cee776c0b7f1", "decree"),
    ("789d1346-9a1b-4f9c-b166-d825cdb313f4", "constitution"),
    ("cf65aecc-49c1-4054-b35b-fd581ea723e9", "ci"), ("0465c7d3-9516-4f7b-baf7-0c5b6ed3ee10", "ci"),
    ("8240d802-757b-46b6-8505-8d529127227b", "ci"), ("2c264e8d-6101-4424-9e76-669b4cfaf244", "ci"),
    ("38686311-0971-45ea-b395-4fd40b8e9540", "ci"),
    ("a7bdb327-ad42-4ed6-8bc2-5ee4a0393d60", "li"), ("715ddbd7-caef-4f3a-ba83-282db2c52f80", "li"),
    ("a6a1ce99-51ba-4674-83a0-2bd489723112", "li"),
    ("9a491573-b551-48c6-b645-fedef0fc5ff1", "ei"), ("716bd53a-911e-430d-a7bb-118e0cd5699b", "ei"),
]
LOCK = threading.Lock()
_last = [0.0]
STOP = threading.Event()
LOG = open(ROOT / "progress.log", "a", encoding="utf8", buffering=1)
CACHE.mkdir(exist_ok=True)
REQ = open(CACHE / "requests.jsonl", "a", encoding="utf8", buffering=1)


def log(msg):
    with LOCK:
        LOG.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + msg + "\n")


def get(url, timeout=120):
    back = 30
    for attempt in range(7):
        if STOP.is_set():
            return None
        with LOCK:
            wait = _last[0] + 0.25 - time.time()
            _last[0] = max(time.time(), _last[0] + 0.25)
        if wait > 0:
            time.sleep(wait)
        code, body = None, b""
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                code, body = r.status, r.read()
        except urllib.error.HTTPError as e:
            code = e.code
            try:
                body = e.read()
            except Exception:
                pass
        except Exception as e:
            code = f"ERR {type(e).__name__}"
        with LOCK:
            REQ.write(json.dumps({"t": round(time.time(), 1), "url": url, "code": code, "bytes": len(body)}) + "\n")
        if code == 200:
            if b"Just a moment" in body[:3000] and b"cf_chl" in body:
                log(f"STOP challenge {url}")
                STOP.set()
                return None
            return body
        if code == 404:
            log(f"404 {url}")
            return None
        if code in (401, 403):
            log(f"STOP {code} {url}")
            STOP.set()
            return None
        log(f"retry {code} {url} sleep {back}")
        time.sleep(back)
        back = min(back * 2, 600)
    log(f"GAVE UP {url}")
    return None


def catalogue():
    out = ROOT / "catalogue.jsonl"
    seen = set()
    if out.exists():
        for l in out.read_text("utf8").splitlines():
            seen.add(json.loads(l)["uuid"])
    done_scopes = ROOT / "catalogue.scopes"
    done = set(done_scopes.read_text().split()) if done_scopes.exists() else set()
    f = open(out, "a", encoding="utf8", buffering=1)
    for scope, kind in SCOPES:
        if scope in done:
            continue
        page, n = 0, 0
        while not STOP.is_set():
            b = get(f"{API}/discover/search/objects?scope={scope}&dsoType=ITEM&size=100&page={page}")
            if not b:
                break
            sr = json.loads(b)["_embedded"]["searchResult"]
            objs = [o["_embedded"]["indexableObject"] for o in sr["_embedded"]["objects"]]
            new = [it for it in objs if it["uuid"] not in seen]

            def one(it):
                x = get(f"{API}/core/items/{it['uuid']}?embed=bundles/bitstreams")
                if not x:
                    return None
                x = json.loads(x)
                bs = []
                for bd in x["_embedded"]["bundles"]["_embedded"]["bundles"]:
                    if bd["name"] in ("ORIGINAL", "TEXT"):
                        for s in bd["_embedded"]["bitstreams"]["_embedded"]["bitstreams"]:
                            bs.append({"bundle": bd["name"], "name": s["name"], "size": s["sizeBytes"],
                                       "uuid": s["uuid"], "url": s["_links"]["content"]["href"]})
                md = {k: [v["value"] for v in vs] for k, vs in it["metadata"].items()}
                return {"uuid": it["uuid"], "name": it["name"], "handle": it.get("handle"), "scope": scope,
                        "kind": kind, "md": md, "bitstreams": bs}

            with ThreadPoolExecutor(4) as ex:
                for rec in ex.map(one, new):
                    if rec:
                        seen.add(rec["uuid"])
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        n += 1
            if page + 1 >= sr["page"]["totalPages"]:
                with open(done_scopes, "a") as d:
                    d.write(scope + "\n")
                break
            page += 1
        log(f"catalogue {kind} {scope}: {n} new items")
    log("catalogue done")


def pdfs():
    recs = [json.loads(l) for l in (ROOT / "catalogue.jsonl").read_text("utf8").splitlines()]
    order = {k: i for i, k in enumerate(["constitution", "act", "decree", "ci", "li", "ei"])}
    recs.sort(key=lambda r: order[r["kind"]])
    (CACHE / "pdf").mkdir(exist_ok=True)
    jobs = []
    import re
    recs = [r for r in recs if not re.search(r"Bill|Report of|Memorandum|Instructions for", r["name"], re.I)]
    for r in recs:
        for s in r["bitstreams"]:
            if s["bundle"] != "ORIGINAL" or not s["name"].lower().endswith(".pdf") or s["size"] > 120_000_000:
                continue
            p = CACHE / "pdf" / f"{s['uuid']}.pdf"
            if not p.exists():
                jobs.append((s["url"], p))
    log(f"pdfs: {len(jobs)} to fetch")

    def one(j):
        url, p = j
        b = get(url, timeout=600)
        if b:
            tmp = p.with_suffix(".tmp")
            tmp.write_bytes(b)
            tmp.replace(p)
        return bool(b)

    k = 0
    with ThreadPoolExecutor(4) as ex:
        for ok in ex.map(one, jobs):
            k += 1
            if k % 50 == 0:
                log(f"pdfs {k}/{len(jobs)}")
    log("pdfs done")


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("all", "catalogue"):
        catalogue()
    if stage in ("all", "pdfs") and not STOP.is_set():
        pdfs()
