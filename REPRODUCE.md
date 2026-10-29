# How this repository was made (Ghana)

This file is written by the build on 2026-10-29, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| GhaLII, the Ghana Legal Information Institute (on the Laws.Africa Peachjam platform) | <https://ghalii.org> | 2026-10-28 | CC BY-NC 4.0, crediting GhaLII as the source (https://ghalii.org/terms-of-use/, s. 9: "you may freely use, re-use and redistribute works from GhaLII provided you credit GhaLII as your source and your use is not for commercial gain") |
| Internet Archive Wayback Machine | <https://web.archive.org> | 2026-10-28 | Archived copies of GhaLII pages; the content licence is GhaLII's |
| Ghana Publishing Company (Assembly Press): Cybersecurity Act, 2020 (Act 1038) | <https://dataprotection.org.gh/wp-content/uploads/2025/05/Cybersecurity-Act-2020-Act-1038_2.pdf> | 2026-10-29 | Act of the Parliament of the Republic of Ghana as printed by the Assembly Press; the copy states no licence. |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `data-protection` | Data Protection Act, 2012 | 1 | 2012-10-16 to 2012-10-16 |
| `companies` | Companies Act, 2019 | 1 | 2019-08-02 to 2019-08-02 |
| `renewable-energy` | Renewable Energy Act, 2011 | 2 | 2011-12-31 to 2020-12-29 |
| `cybersecurity` | Cybersecurity Act, 2020 (Act 1038) | 1 | 2020-12-29 to 2020-12-29 |

The build made 5 commits:

| Commits | Kind |
| ---: | --- |
| 4 | first version of an act |
| 1 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `future`: laws not yet in force on 2026-10-29.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 5 laws in the record.
- 10 tags.

## Dates

Each commit is dated at noon (Africa/Accra) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: Not applied: every version is dated by the commencement date GhaLII states for the act or for the amending Act (Act 527 of 1996: "Commenced" 31 December 1996, the day of its Gazette notification), or, for the Constitution as made, by section 1 of the Constitution of the Fourth Republic of Ghana (Promulgation) Law, 1992 (P.N.D.C.L. 282): in force on 7 January 1993. No date is computed from a default rule. https://ghalii.org/legislation/

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `584b5f69348473021a5611cb62db3954c5df5391b85b46832aa3596fe28c0ef8` (1064977 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `a4faa25af85facb64b956b372f6b528aafdd7ec1`, `check.py` `3d00541d258745461ab52b1b0cb4e1716a27a95d`, `on.py` `644a6c0857fbcc72562032b58d57aa113fee0641`.
- Python 3.12.10; git version 2.46.0.windows.1.

## Checks

5 versions of 4 acts read back from git on the day each took effect and on the day before: 0 mismatches. Trailers: 0 commits whose trailers git cannot parse. Health: 0 merge commits on main, 0 commit dates that go backwards, 0 commits dated after the build.

A second build from the same corpus into an empty folder gave identical hashes for all 5 history commits and 10 tags (history tip `b628a02ad9fd936933840cd6de99449e4190f879`).

## Decisions made by hand

- Acts were chosen by what the archive holds. Of the 748 GhaLII works the Internet Archive holds, only three have more than one expression archived, and the 1992 Constitution has none. The Data Protection Act 2012 and the Companies Act 2019 have one expression each, and GhaLII's History for each lists no amendment (applied or not yet applied), so the single version is the whole history GhaLII records. The Renewable Energy Act 2011 has both of its expressions archived (2011 and 2020).
- The Labour Act 2003 (Act 651) was not taken: both archived copies of its only expression carry no Akoma Ntoso text (GhaLII shows only the source PDF), and no OCR is used. The Criminal Offences Act 1960 (Act 29) has no archived GhaLII expression page at all.
- Licence: GhaLII licenses its primary and secondary law content CC BY-NC 4.0 with attribution (terms s. 9); CC BY-NC allows only non-commercial use. Every GhaLII version is read from the Internet Archive's copy, for the configured acts only. GhaLII's terms (s. 7) say it converts most documents with OCR software; its text is used as GhaLII publishes it, and no OCR was run here. No legal text was given to a model.
- Renewable Energy Act: the 2011 expression's coverpage says only "Commenced" with no date, so the adapter keeps its expression date, 31 December 2011; GhaLII's 2020 expression of the same act states "Commenced on 31 December 2011", the same day.
- Version dates are GhaLII's expression dates. Laws.Africa's terminology guide (https://docs.laws.africa/getting-started/terminology-guide) says "Amendments to Principal works come into force on the Commencement date of the Amending work" and that the first point in time is "the work as originally published"; so an amendment's expression is dated by its commencement (in force), and an act's original expression by its publication, which is replaced by the commencement date the page states.
- Credits: a version whose History names exactly one amending law (and no consolidation) between it and the previous version is credited to that law for every provision that changed. Otherwise a provision is credited only to laws that GhaLII's editorial note inside that provision links to; the rest are unexplained (publisher).
- Editorial notes (akn-remark) are left out of the text and used only as credit evidence, except where a provision has no other text (repealed or spent), where the note is the provision's whole printed content.
- Part, Chapter and Division headings are left out; each provision file starts with its own number and heading. Every other text of each version is in a provision file: this is checked per version (verification.json, fidelity).
- DPA 2012: the first version is dated 2012-10-16, the commencement date GhaLII states ("Commenced on 16 October 2012"), not 2012-05-18, the date of its expression (Gazette publication).
- Renewable Energy Act: GhaLII gives no single commencement date (Commenced); the first version keeps its expression date 2011-12-31, the Gazette publication.
- Cybersecurity Act, 2020 (Act 1038): one version, the Act as passed, dated 29 December 2020: the print gives "DATE OF ASSENT: 29th December, 2020" and "Date of Gazette notification: 29th December, 2020", and the Act has no commencement section; the version is dated by that day.
- Cybersecurity Act, 2020: no amending Act was found; the Data Protection Commission publishes this print as the Act (May 2025 upload), so the enacted text is taken as today's text.
- Cybersecurity Act, 2020: read from the print's text layer: each section's bold heading is its file's first line; the italic group headings ("Cyber Security Authority", "Miscellaneous Provisions", ...) are left out and listed in verification-batch2.json; every printed word from "PASSED by Parliament" to the printer's colophon is in a provision file or a dropped group heading, and none is added.
- Cybersecurity Act, 2020: the Second Schedule's table of administrative penalties is read line by line as printed, its cells joined by " | ", without reassembling rows. One printed line, where two cells overlap on the page, is put back in print order ("76(12) | Service provider who | Ten thousand penalty units.").
- Cybersecurity Act, 2020: section 99(2) prints the new Extradition Act entry with the Act number left blank ("(Act .............)"); kept as printed.

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- Claude Code (Claude Opus 5.5, claude-opus-5-5) wrote the configuration and the Constitution reader, and chose the acts. No model wrote, summarised or transformed legal text: the text is parsed by deterministic code.
- Claude Code (Claude Opus 5.5, claude-opus-5-5) wrote Lexifina's code and chose the source. No model wrote, summarised or transformed legal text: the reader is deterministic code reading the PDF's text layer.
