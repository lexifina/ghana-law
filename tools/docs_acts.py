"""Add the Acts of Parliament (Parliament of Ghana repository) to repo/README.md, README.extra.md, repo/LICENSE and
repo/jurisdiction.json, between markers, from the published parts (corpus.d/30-acts-*.json with a .PUBLISH).

    python -X utf8 docs_acts.py
"""
import json
import re
from pathlib import Path

H = Path(__file__).resolve().parent
parts = sorted(p for p in (H / 'corpus.d').glob('30-acts-*.json') if p.with_suffix('.PUBLISH').exists())
acts = [a for p in parts for a in json.loads(p.read_text('utf-8'))['acts']]
acts.sort(key=lambda a: (a['versions'][0]['from'], a['slug']))
n = len(acts)
units = sum(len(a['versions'][0]['units']) for a in acts)
years = sorted({a['versions'][0]['from'][:4] for a in acts})
rows = '\n'.join(f"| `{a['slug']}/` | [{a['title']}]({a['url']}) | {a['versions'][0]['from']} |" for a in acts)
A0, A1 = '<!-- acts:start -->', '<!-- acts:end -->'
SECTION = f"""{A0}
## Acts of Parliament from the Parliament of Ghana

{n} Acts of Parliament as passed ({years[0] if years else ''} to {years[-1] if years else ''}), {units:,} files, one folder per Act named by its number (`act-0651/` is the Labour Act, 2003 (Act 651)). Each is one version, the Act as passed, dated by the date of assent printed on it; where an Act comes into force later (a commencement section, an Executive Instrument), that later day is not shown. Later amending Acts are their own folders; their changes are not replayed into the Acts they amend.

**Source.** The Parliament of Ghana Library publishes typed editions of the Acts (PDFs made from Microsoft Word, with a text layer) in its repository, [repository.parliament.gh](https://repository.parliament.gh/). Each Act here is read from that edition; no OCR. The Library's consolidated editions, marked "As amended by", are not used, and nor are the scanned prints, which have no usable text layer.

**How it was checked.** Every word from "AN ACT" to the Gazette notification line is in a file, checked letter for letter, except page numbers, footnote markers and the Part and group headings printed above sections; each section's title is its file's first line. An Act whose sections are not numbered 1, 2, 3 and so on without a gap is left out. The typed edition is a re-keyed text, not a facsimile of the Assembly Press print: read the same way, the Library's edition of the Cybersecurity Act, 2020 has the same words as the Assembly Press print in `cybersecurity/` in 62 of its 103 provisions, and the others differ by a punctuation mark, a paragraph letter or a typing slip (all at least 99.7% the same).

| Folder | Act | Assent |
| --- | --- | --- |
{rows}
{A1}"""


def put(path: Path, text: str, anchor: str | None) -> None:
    s = path.read_text('utf-8') if path.exists() else ''
    if A0 in s:
        s = re.sub(re.escape(A0) + '.*?' + re.escape(A1), lambda m: text, s, flags=re.S)
    elif anchor and anchor in s:
        s = s.replace(anchor, text + '\n\n' + anchor, 1)
    else:
        s = s.rstrip('\n') + '\n\n' + text + '\n'
    path.write_text(s, 'utf-8', newline='\n')


put(H / 'repo' / 'README.md', SECTION, '## A lawyer\'s questions as git commands')
put(H / 'README.extra.md', SECTION, None)
LIC = f"""{A0}
Acts of Parliament in the folders act-NNNN/: the Parliament of Ghana Library's typed editions of Acts of the
Parliament of the Republic of Ghana, from its repository (https://repository.parliament.gh/), retrieved 2026-11-03.
The repository states no licence or terms. Under the Copyright Act, 2005 (Act 690), section 3, copyright in works
made for the Government vests in the Government. The texts are reproduced without change to their wording, as the
law of Ghana. Neither the Parliament of Ghana nor its Library endorses this repository.
{A1}"""
put(H / 'repo' / 'LICENSE', LIC, 'Lexifina\'s own contributions')
j = json.loads((H / 'repo' / 'jurisdiction.json').read_text('utf-8'))
base = j['build'].split('; plus ')[0]
j['build'] = base + f'; plus {n} Acts of Parliament as passed ({years[0] if years else ""}-{years[-1] if years else ""}), from the Parliament of Ghana Library repository'
(H / 'repo' / 'jurisdiction.json').write_text(json.dumps(j, ensure_ascii=False, indent=2) + '\n', 'utf-8', newline='\n')
print(n, 'acts', units, 'units')
