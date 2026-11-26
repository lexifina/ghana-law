# Structure

Every law is a folder by kind and year, with one file per provision. No folder holds more than 1,000 entries.

```
acts/<year>/<number>-<short name>/     Acts of Parliament, by year of the Act and Act number
    README.md                          the Act's title, source and list of provisions
    preamble.md                        long title, date of assent and enacting words
    sec-001.md ... sec-NNN.md          one file per section ("sec-012a.md" for an inserted section 12A)
    schedule-01.md ...                 one file per Schedule
constitution/                          the Constitution of 1992: art-NNN.md per article, preamble.md, schN-... per Schedule
subsidiary/<year>/<kind>-<number>-<short name>/   Executive Instruments (ei-9-creation-districts); no Legislative or
                                       Constitutional Instruments yet
data/                                  tables: laws.csv, paths.json (act id -> folder), versions and commits
tools/                                 the scripts that built this history
```

- `<year>` is the year in the Act's title; `<number>` is the Act number (`acts/2003/651-labour/` is the Labour Act, 2003 (Act 651)).
  An Act of 1957, before Acts were numbered in one series, uses its number for that year (`acts/1957/no-17-...`).
  An Executive Instrument's `<year>` is the year it was made.
- `<short name>` is the title in lower case with "Act", the year and small words (the, of, and, for, on, to, in, a) left out.
- A section file starts with `# <number>. <title>` and then the section's text, one paragraph per subsection or item.

## Commits

- One commit per version of an Act: for an Act as passed, the Act itself, credited to the Act (`Act 651`); for an
  Executive Instrument, the Instrument (`E.I. 9 of 2003`); for a consolidation, its publisher.
- A text copied from a secondary source (no official copy with a usable text layer was found) carries
  `Source-status: secondary copy (<source>, <address>)`.
- Dated at noon Africa/Accra (UTC+0) on the day the version took effect, with that day in the `In-force:` trailer and the
  reason in `In-force-basis:` (a commencement section, else the date of assent). Git cannot store dates before 1970:
  those commits are dated from 1 January 1970, one second apart, and the real day is in `In-force:`.
- Other trailers: `Law:`, `Kind:`, `Enacted:` (date of assent), `Published:` (Gazette notification), `Source:`,
  `Source-file:`, `Source-sha256:`, `Text-source:`, `Act:`, `Provisions:`.

Until 26 November 2026 Acts were in `act/<year>/<number>/`, and until 11 November 2026 in folders named by the Act's id
(`act-0651/`); `git log --follow` follows the files through both moves and `data/paths.json` maps each id to its folder.
