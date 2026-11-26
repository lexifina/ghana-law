"""Compare the preview branch's 1996 Constitution (OSP text) article by article with Constitute's text."""
import os
import json, re, html, subprocess, difflib, collections
REPO = os.path.join(os.environ.get("GH_ACQ", "."), 'repo')
h = json.load(open(os.path.join(os.environ.get("GH_ACQ", "."), 'sec/cache/constitute_gh.html'), encoding="utf8"))["html"]
# split Constitute into articles on h3 "N. Title"
txt = re.sub(r"<p>(?=\d{1,3}\.\s)", "\n@@HEAD ", h)
txt = re.sub(r"<(h[1-6])[^>]*>", "\n@@HEAD ", txt)
txt = re.sub(r"</(p|li|h[1-6]|div)>", "\n", txt)
txt = html.unescape(re.sub(r"<[^>]+>", " ", txt))
cons, cur = {}, None
for line in txt.split("\n"):
    line = re.sub(r"\s+", " ", line).strip()
    if not line:
        continue
    m = re.match(r"@@HEAD (\d{1,3})\.\s*(.*)", line)
    if m:
        cur = int(m.group(1))
        if cur in cons:  # schedules restart numbering; keep the first (articles)
            cur = None
            continue
        cons[cur] = []
        continue
    if line.startswith("@@HEAD"):
        if re.search(r"SCHEDULE", line, re.I):
            break
        continue
    if cur:
        cons[cur].append(line)
files = subprocess.run(["git", "-C", REPO, "ls-tree", "--name-only", "origin/preview", "constitution/"],
                       capture_output=True, text=True).stdout.split()
W = lambda s: [w for w in re.findall(r"[a-z0-9]+", s.lower()) if not re.fullmatch(r"\d+|[a-z]|[ivx]+", w)]
import zipfile, io
_arch = subprocess.run(["git", "-C", REPO, "archive", "--format=zip", "origin/preview", "constitution/"],
                       capture_output=True).stdout
ZIP = zipfile.ZipFile(io.BytesIO(_arch))
stats, worst = [], []
for f in files:
    m = re.match(r"constitution/art-(\d{3})\.md", f)
    if not m:
        continue
    n = int(m.group(1))
    ours = ZIP.read(f).decode("utf8")
    body = ours.split("\n", 1)[1] if "\n" in ours else ""
    a, b = W(body), W(" ".join(cons.get(n, [])))
    r = difflib.SequenceMatcher(None, a, b, autojunk=False).ratio() if (a or b) else 1.0
    stats.append((n, r, len(a), len(b)))
    if r < 0.98:
        worst.append((round(r, 3), n, len(a), len(b)))
        sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
        print(n, [(op, " ".join(a[i1:i2]), " ".join(b[j1:j2])) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != "equal"][:6])
print("articles", len(stats), "constitute articles", len(cons))
c = collections.Counter("1.0" if r == 1 else ">=.99" if r >= .99 else ">=.98" if r >= .98 else ">=.95" if r >= .95 else "<.95"
                        for _, r, _, _ in stats)
print(c)
print(sorted(worst)[:40])
