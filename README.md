# Ghana: law history in git

The law of Ghana as a git history: one file per provision, one commit per law on the day it took effect, and the law that made each change as the commit's author. `git blame` names the law behind every paragraph; `git log` lists every change to a provision; `tools/on.py` gives the text in force on any day.

It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law), which places it at `gh/`. Every version is a dated point-in-time version published by [GhaLII](https://ghalii.org) on the Laws.Africa Peachjam platform.

**What is in it now**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `data-protection/` | [Data Protection Act, 2012](https://ghalii.org/akn/gh/act/2012/843) | 1 | 2012-10-16 to 2012-10-16 |
| `companies/` | [Companies Act, 2019](https://ghalii.org/akn/gh/act/2019/992) | 1 | 2019-08-02 to 2019-08-02 |
| `renewable-energy/` | [Renewable Energy Act, 2011](https://ghalii.org/akn/gh/act/2011/832) | 2 | 2011-12-31 to 2020-12-29 |
| `cybersecurity/` | [Cybersecurity Act, 2020 (Act 1038)](https://dataprotection.org.gh/wp-content/uploads/2025/05/Cybersecurity-Act-2020-Act-1038_2.pdf) | 1 | 2020-12-29 to 2020-12-29 |

**Data Protection Act, 2012**

| In force | Author |
| --- | --- |
| 2012-10-16 | Act 843 of 2012 (as enacted) |

**Companies Act, 2019**

| In force | Author |
| --- | --- |
| 2019-08-02 | Act 992 of 2019 (as enacted) |

**Renewable Energy Act, 2011**

| In force | Author |
| --- | --- |
| 2011-12-31 | Act 832 of 2011 (as enacted) |
| 2020-12-29 | Act 1045 of 2020 |

Each folder's `README.md` lists every provision, how often it changed and when.

## The Cybersecurity Act, 2020

`cybersecurity/` holds the Cybersecurity Act, 2020 (Act 1038) as passed, in force from 29 December 2020 (its date of assent and of Gazette notification; the Act has no commencement section). It is read from the Assembly Press print (Ghana Publishing Company) published by the Data Protection Commission, with a text layer (no OCR): every printed word from the enacting words to the printer's colophon is in a provision file or a group heading, and none is added. No amending Act was found, so the text is taken as today's text. The Second Schedule's penalty table is read line by line as printed, cells joined by " | ".

## A lawyer's questions as git commands

| Question | Command |
| --- | --- |
| What did sec-001 say on 2012-10-16? | `python tools/on.py 2012-10-16 data-protection sec-001` |
| The same, with raw git (bash) | `git show $(git rev-list -1 --before="2012-10-16T23:59:59Z" main -- data-protection/sec-001.md):data-protection/sec-001.md` |
| The same, in PowerShell | `$r = git rev-list -1 --before="2012-10-16T23:59:59Z" main -- data-protection/sec-001.md; git show "$($r):data-protection/sec-001.md"` |
| Which law wrote each line? | `git blame data-protection/sec-001.md` |
| Every change, word by word | `git log -p --word-diff data-protection/sec-001.md` |
| Every law in the record, in order | `git log --reverse --format="%ad %an" --date=short main` |
| Everything one law changed | `git show law/<key>` (tags `law/<key>` mark each law's commit) |
| The whole act on a date | `python tools/on.py 2012-10-16 data-protection` |
| Which law gave a provision its wording on a date | `python tools/on.py --law 2012-10-16 data-protection sec-001` |

After a rebuild, refresh tags with `git fetch --force --tags`: a plain fetch keeps stale tags.

## Dates

- Each commit is dated at **noon, Africa/Accra, on the day the change took effect**. The day is also in the `In-force:` trailer, which the tools read; enactment (assent) and Gazette publication dates are trailers too, where GhaLII states them.
- **The day is GhaLII's.** Each version is a Laws.Africa expression, and its date is the day the amendment it takes in came into force, as the amendment list says ("[Amended by <Act> on <date>]"). For a consolidation (a revised edition) it is the date the edition is as at. An act's original expression is dated by its Gazette publication; where GhaLII gives a later commencement date ("Commenced on ..."), the first version is dated by that instead (see REPRODUCE.md, decisions).
- `--before="YYYY-MM-DD"` alone uses your clock's time of day, so a law that took effect that day may be missed before noon. Use `T23:59:59Z` as above, or the tool.

## How it is checked

- Every version is read back from git on the day it took effect and on the day before (`tools/check_repo.py`); both must match `corpus.json`. Results are in `REPRODUCE.md`.
- **Against GhaLII today:** the last version of each act is GhaLII's current expression, as named by its own legislation listing on the retrieval day, and is the text of that expression page.
- **Every version is its own dated expression**: each was parsed from an archived copy of exactly that expression's page, whose sha256 is recorded with the version.
- The repository is rebuilt from the same data a second time and must give identical hashes.

## What "author" means

The author of a commit is the law that made the change, with an e-mail address that cannot exist, so `git blame` and `git log --author` name laws. The committer is always Lexifina.

- **Credits come only from GhaLII's own notes.** A version whose History entry names one amending Act is credited to it. Where one version takes in several Acts, or a revised edition, a provision is credited to an Act only if GhaLII's editorial note in that provision names it ("[section 5 amended by section 2 of Act 3 of 2020]"); the rest are committed by the publisher and labelled "unexplained", and the commit message names the Acts the version takes in.
- **The first commit** is the act as enacted where that is the oldest version; otherwise it is the oldest version available (a consolidation), credited to the publisher.
- Blame credits whole lines (one paragraph per line). Use `git log -p --word-diff` to see exactly which words each change made.

## What it does not show

- **Only the versions GhaLII publishes.** Changes before its oldest version are not separate commits.
- **Editorial notes.** GhaLII's bracketed notes ("[Act No. 18 of 1996]", "[section 5 amended by ...]") are left out of the text and used only for credits, except where a provision has no other text (repealed or spent), where the note is what GhaLII prints and is kept.
- **Headings above the provision** (Part, Chapter, Division) are left out; each file starts with its own number and heading. Footnotes are kept at the end of the file.
- **Amendments not yet applied.** Where the LII lists an amendment as not yet applied to its consolidated text, it is not in this history; REPRODUCE.md lists each one.
- **No OCR.** Acts the LII shows only as scanned PDFs are not included.

## The Constitution (preview branch only)

`constitution/` holds the Constitution of the Republic of Ghana, 1992, in two versions: as made, in force from 7 January 1993 (section 1 of the Constitution of the Fourth Republic of Ghana (Promulgation) Law, 1992, P.N.D.C.L. 282), and as amended by the Constitution of the Republic of Ghana (Amendment) Act, 1996 (Act 527), from 31 December 1996. No later amendment has been made.

It is not a GhaLII text: the Internet Archive holds no GhaLII page of the 1992 Constitution. Both versions are read from government-hosted PDFs with a text layer (no OCR):

- the Office of the Special Prosecutor's "Constitution of the Republic of Ghana, 1992 (as Amended to 1996)" ([osp.gov.gh](https://osp.gov.gh/media/Resources/Ghana_Constitution.pdf)), a compilation marked Oceana that brackets each passage Act 527 changed and names the section of the Act in an endnote: the 1996 text, and every provision Act 527 left alone;
- the Audit Service's copy of the 1992 text ([audit.gov.gh](https://audit.gov.gh/files/publications/The_1992_Constitution_of_the_Republic_of_Ghana635603143.pdf)): only the wording of the nine articles Act 527 changed (8, 9, 112, 114, 166, 199, 201, 206, 211), for the 1993 version.

Neither is a Government Printer (Assembly Press) edition, so the Constitution is kept on the `preview` branch, off `main`, until its text can be checked against an official print. Every provision Act 527 changed is credited to it; the other 290 articles, the Preamble and the Schedules are the same in both versions.

## How it is built

Lexifina reads the sources listed here and records each act's dated versions, and the laws that made each change, in one corpus file. `tools/build.py` writes this repository from that file, and the same corpus always gives the same commit hashes; `REPRODUCE.md` gives the details and the checks. A model (Claude) wrote Lexifina's code; it wrote no legal text, and no model runs when the history is built.

The parser splits the Akoma Ntoso HTML into one file per provision, takes dates and credits from the LII's History tab, amendment list and editorial notes, and writes `corpus.json`; the shared builder `tools/build.py` turns that into the commits.

## Sources

| Source | What it gives | Used for |
| --- | --- | --- |
| [GhaLII](https://ghalii.org) | Dated point-in-time versions (expressions) of each act, its History and amendment list, and per-provision editorial notes; its listing page names the current version | The text and dates of every version |
| [Internet Archive](https://web.archive.org/) | Archived copies of those expression pages | Reading them |

## Licence

See [LICENSE](LICENSE). Source: GhaLII, the Ghana Legal Information Institute (https://ghalii.org), licensed under the Creative Commons Attribution-NonCommercial 4.0 International licence (CC BY-NC 4.0).

GhaLII's terms: CC BY-NC 4.0, crediting GhaLII as the source (https://ghalii.org/terms-of-use/, s. 9: "you may freely use, re-use and redistribute works from GhaLII provided you credit GhaLII as your source and your use is not for commercial gain"). Lexifina's arrangement, messages, tables and tools are CC0.

This repository is not legal advice. Ghana's laws are published in English, so there is no separate summary in another language.
