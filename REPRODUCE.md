# How this repository was made (Ghana)

This file is written by the build on 2026-10-28, the day the source data was retrieved. Everything below is enough to rebuild this repository hash for hash.

## Sources

| Source | Address | Retrieved | Requests | Licence |
| --- | --- | --- | ---: | --- |
| GhaLII, the Ghana Legal Information Institute (on the Laws.Africa Peachjam platform) | <https://ghalii.org> | 2026-10-28 | 31 | CC BY-NC 4.0, crediting GhaLII as the source (https://ghalii.org/terms-of-use/, s. 9: "you may freely use, re-use and redistribute works from GhaLII provided you credit GhaLII as your source and your use is not for commercial gain") |
| Internet Archive Wayback Machine | <https://web.archive.org> | 2026-10-28 | None | Archived copies of GhaLII pages; the content licence is GhaLII's |
| Office of the Special Prosecutor, Ghana: The Constitution of the Republic of Ghana, 1992 (as Amended to 1996) | <https://osp.gov.gh/media/Resources/Ghana_Constitution.pdf> | 2026-10-28 | None | Government of Ghana website; no licence stated. The compilation is marked "Oceana" (Constitutions of the Countries of the World); the constitutional text itself is Ghana's law. |
| Ghana Audit Service: The 1992 Constitution of the Republic of Ghana | <https://audit.gov.gh/files/publications/The_1992_Constitution_of_the_Republic_of_Ghana635603143.pdf> | 2026-10-28 | None | Government of Ghana website; no licence stated. |

Every response is cached by the sha256 of its URL, and the table above lists every source with its retrieval date. Lexifina keeps its fetch scripts privately; `tools/parse.py` reads only the cache and writes `corpus.json`, so the same cache always gives the same corpus.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `data-protection` | Data Protection Act, 2012 | 1 | 2012-10-16 to 2012-10-16 |
| `companies` | Companies Act, 2019 | 1 | 2019-08-02 to 2019-08-02 |
| `renewable-energy` | Renewable Energy Act, 2011 | 2 | 2011-12-31 to 2020-12-29 |
| `constitution` | Constitution of the Republic of Ghana, 1992 | 2 | 1993-01-07 to 1996-12-31 |

The build made 6 commits:

| Commits | Kind |
| ---: | --- |
| 4 | first version of an act |
| 2 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `future`: laws not yet in force on 2026-10-28.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 6 laws in the record.
- 12 tags.

## Dates

Each commit is dated at noon (Africa/Accra) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Not applied: every version is dated by the commencement date GhaLII states for the act or for the amending Act (Act 527 of 1996: "Commenced" 31 December 1996, the day of its Gazette notification), or, for the Constitution as made, by section 1 of the Constitution of the Fourth Republic of Ghana (Promulgation) Law, 1992 (P.N.D.C.L. 282): in force on 7 January 1993. No date is computed from a default rule. https://ghalii.org/legislation/

## Commands, in order

```sh
# fill the cache from the sources listed above (network; Lexifina's fetch scripts are kept privately)
python -X utf8 tools/parse.py                  # cache -> corpus.json (no network)
python -X utf8 tools/build.py <folder> --repo <empty folder> --docs-date 2026-10-28
python -X utf8 tools/check_repo.py <repo> --corpus <folder>/corpus.json --write
python -X utf8 tools/build.py <folder> --repo <another empty folder> --docs-date 2026-10-28 --compare <repo>
```

In the main Lexifina repository these files live as follows:
- `fetch.py`, `parse.py` and `repo/`: in `scripts/ghana-law/`.
- `build.py`, `check_repo.py` (`check.py` there) and `on.py`: in `scripts/gitlaw_common/`, with the corpus format in `SCHEMA.md`.

## Exact inputs

- `corpus.json` sha256 `beb606438cfe76b4d8e672c66db468221e89ad7965a7256d4819f20af63523b6` (1325405 bytes)
- Script blob hashes (`git hash-object`):

| Script | Blob |
| --- | --- |
| build.py | `2bfc4ac9df193a7be844556d7f69cdb9d93ec3f2` |
| check.py | `cd346c7ff9996d450240e3bab52bcae03b2bc865` |
| on.py | `644a6c0857fbcc72562032b58d57aa113fee0641` |
| fetch.py | `91ad09fe757ebee9568af610f5cc17fbb823be56` |
| parse.py | `3eaa6becb63a43f6f70d36e31bde7cd22ae2a1b2` |

- Tools:
  - Python 3.14.0
  - git version 2.52.0.windows.1
  - curl 8.21.0 (Windows) libcurl/8.21.0 Schannel zlib/1.3.2 WinIDN WinLDAP

## Checks

4 versions of 3 acts read back from git on the day each took effect and on the day before: 0 mismatches. Trailers: 0 commits whose trailers git cannot parse. Health: 0 merge commits on main, 0 commit dates that go backwards, 0 commits dated after the build.

Not yet run for this build.

These results are from the check run on the build before this one, from the same corpus.

## Decisions made by hand

- Acts were chosen by what the archive holds. Of the 748 GhaLII works the Internet Archive holds (one CDX query, 2026-10-28), only three have more than one expression archived, and the 1992 Constitution has none. The Data Protection Act 2012 and the Companies Act 2019 have one expression each, and GhaLII's History for each lists no amendment (applied or not yet applied), so the single version is the whole history GhaLII records. The Renewable Energy Act 2011 has both of its expressions archived (2011 and 2020).
- The Labour Act 2003 (Act 651) was not taken: both archived copies of its only expression carry no Akoma Ntoso text (GhaLII shows only the source PDF), and no OCR is used. The Criminal Offences Act 1960 (Act 29) has no archived GhaLII expression page at all.
- Licence and terms: GhaLII licenses its primary and secondary law content CC BY-NC 4.0 with attribution (terms s. 9), and its terms prohibit scraping and bulk downloading from its website (s. 4); its robots.txt sends Content-Signal ai-train=no, ai-input=no and Crawl-delay 5. No GhaLII document page was fetched: every GhaLII version is read from the Internet Archive's copy, through the shared machine-wide archive.org rate, for the configured acts only. The user decided on 2026-10-28 that reading these archived copies is acceptable (relayed by the coordinator: "scraping wayback is fair game, dont overdo it"). GhaLII's terms (s. 7) say it converts most documents with OCR software; its text is used as GhaLII publishes it, and no OCR was run here. The repository stays private; CC BY-NC allows only non-commercial use. No legal text was given to a model.
- Renewable Energy Act: the 2011 expression's coverpage says only "Commenced" with no date, so the adapter keeps its expression date, 31 December 2011; GhaLII's 2020 expression of the same act states "Commenced on 31 December 2011", the same day.
- Version dates are GhaLII's expression dates. Laws.Africa's terminology guide (https://docs.laws.africa/getting-started/terminology-guide) says "Amendments to Principal works come into force on the Commencement date of the Amending work" and that the first point in time is "the work as originally published"; so an amendment's expression is dated by its commencement (in force), and an act's original expression by its publication, which is replaced by the commencement date the page states.
- Credits: a version whose History names exactly one amending law (and no consolidation) between it and the previous version is credited to that law for every provision that changed. Otherwise a provision is credited only to laws that GhaLII's editorial note inside that provision links to; the rest are unexplained (publisher).
- Editorial notes (akn-remark) are left out of the text and used only as credit evidence, except where a provision has no other text (repealed or spent), where the note is the provision's whole printed content.
- Part, Chapter and Division headings are left out; each provision file starts with its own number and heading. Every other text of each version is in a provision file: parse.py checks this per version (verification.json, fidelity).
- DPA 2012: the first version is dated 2012-10-16, the commencement date GhaLII states ("Commenced on 16 October 2012"), not 2012-05-18, the date of its expression (Gazette publication).
- Renewable Energy Act: GhaLII gives no single commencement date (Commenced); the first version keeps its expression date 2011-12-31, the Gazette publication.
- Constitution: the Internet Archive holds no GhaLII page of the 1992 Constitution, and parliament.gh lists no Constitution among its Acts; the two versions are read from government-hosted PDFs with a text layer (no OCR): the Office of the Special Prosecutor's "Constitution of the Republic of Ghana, 1992 (as Amended to 1996)" (osp.gov.gh, a compilation marked Oceana) and the Audit Service's copy of the 1992 text (audit.gov.gh). Neither is a Government Printer edition.
- Constitution, 1993 version: the 1992 text is rebuilt as the OSP text with the eleven passages it brackets as 1996 amendments (endnotes 1 to 11, naming sections 1 to 9 of Act 527) put back to their 1992 wording from the Audit Service copy: article 8 whole, article 9(5), article 112(5), article 114 whole, "fifteen" in article 166(1), and paragraph (a) of articles 201, 206 and 211; the passages Act 527 only inserted (article 166(1)(a)(ix) to (xi), article 166(3), article 199(4)) are left out. Every other provision is the OSP text in both versions, so the only differences between the versions are the nine articles Act 527 changed.
- Constitution: the 1992 marginal notes of articles 8 and 114, which Act 527 replaced whole, are in neither text source (the Audit Service copy's articles carry no marginal notes, and its arrangement of articles already shows the 1996 ones), so in the 1993 version those two files start "# Article 8" and "# Article 114" with no title.
- Constitution: article titles are the source's own arrangement of articles (title case); the body prints the same titles in capitals. Chapter titles, cross-headings, the Promulgation Law's own sections and its signature ("Made this 8th day of May, 1992") are left out; the Preamble, the 299 articles, the First Schedule's 37 transitional sections and the Second Schedule's oaths are in the provision files.
- Constitution: the OSP compilation keeps Act 527's quotation marks around the new article 8 ("DUAL CITIZENSHIP. ... citizen of Ghana".); they are dropped.
- Constitution: Act 527 is dated by GhaLII's record of it (archived page, Internet Archive capture 20251206102736): assented to 16 December 1996, published and commenced 31 December 1996. GhaLII's own page links Act 527 to the 1960 Constitution under "Amends"; that link is wrong (the Act amends articles 8 to 211 of the 1992 Constitution), and is not used.
- Constitution: GhaLII's source PDF of Act 527 (archived) has a text layer that GhaLII made by OCR (its terms, s. 7); it is used only as a check that the 1996 wording matches the Act (verification.json), never as text.
- Constitution: the Audit Service copy has typing errors in places (e.g. "Parliamentary may make" in article 9(1), "agaisnt" in article 167); only its wording of the nine replaced passages is used, and those passages are listed against the OSP text in verification.json.

## What AI did and did not do

The fetch, parse and check scripts were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above, through code that anyone can rerun.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- Claude Code (Claude Opus 5.5, claude-opus-5-5) wrote the configuration and the Constitution reader (constitution.py), and chose the acts. No model wrote, summarised or transformed legal text: fetch.py, constitution.py and parse.py are deterministic code.
