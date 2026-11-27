"""In-place README / REPRODUCE / LICENSE updates for the Acts added 2026-11-27 from government agency sites."""
import re, shutil, sys
from pathlib import Path
repo = Path(sys.argv[1])


def edit(name, pairs):
    p = repo / name
    t = p.read_text("utf8")
    for old, new in pairs:
        assert t.count(old) == 1, (name, old[:60])
        t = t.replace(old, new)
    p.write_bytes(t.encode("utf8"))


AGENCY = ("the Bank of Ghana, the Ghana Revenue Authority, the Ghana Investment Promotion Authority, the Ghana "
          "Immigration Service, the Ministry of Lands and Natural Resources and the Ministry of Energy")
edit("README.md", [
    ("264 Acts of Parliament from 1957 to 2025", "278 Acts of Parliament from 1957 to 2025"),
    ("249 Acts come from the Parliament of Ghana Library's repository: most as passed,",
     "252 Acts come from the Parliament of Ghana Library's repository: most as passed,"),
    ("and from FAOLEX 5 Acts as passed (among them the Local Governance Act, 2016 and the Economic and Organised Crime "
     "Act, 2010).",
     "and from FAOLEX 5 Acts as passed (among them the Local Governance Act, 2016 and the Economic and Organised Crime "
     "Act, 2010); and 11 Acts from the Assembly Press prints that government bodies publish on their own sites ("
     + AGENCY + ", and the Parliament of Ghana): among them the Customs Act, 2015, the Public Financial Management "
     "Act, 2016, the Banks and Specialised Deposit-Taking Institutions Act, 2016, the Anti-Money Laundering Act, 2008 "
     "and the Stamp Duty Act, 2005 as passed, and the Income Tax Act, 2015 as amended up to Act 973 of 2018."),
    ("- for the two consolidated editions, the Gazette notification day of the amending Act they include (Acts 1038 "
     "and 1031); no earlier text is given;",
     "- for the two consolidated editions, the Gazette notification day of the amending Act they include (Acts 1038 "
     "and 1031); no earlier text is given;\n- for the Income Tax Act, 2015 (Act 896), held as the Ministry of Energy's "
     "consolidation \"as amended by\" eight Acts, the date of assent of the latest of them (Act 973, 31 July 2018);"),
    ("| [Data Protection Commission](https://dataprotection.org.gh) | The Assembly Press print of the Cybersecurity Act, "
     "2020 | no | The Act as passed |",
     "| [Data Protection Commission](https://dataprotection.org.gh) | The Assembly Press print of the Cybersecurity Act, "
     "2020 | no | The Act as passed |\n| Government agency sites: [Bank of Ghana](https://www.bog.gov.gh), "
     "[Ghana Revenue Authority](https://gra.gov.gh), [GIPA](https://gipa.gov.gh), [Immigration Service](https://gis.gov.gh), "
     "[Ministry of Lands](https://mlnr.gov.gh), [Ministry of Energy](https://energymin.gov.gh), "
     "[Parliament](https://www.parliament.gh) | Assembly Press prints of Acts with a text layer | one consolidation | "
     "10 Acts as passed; the Income Tax Act, 2015 as amended up to 2018 |"),
])
edit("LICENSE", [
    ("<!-- acts:end -->",
     "Acts added on 27 November 2026 from the Assembly Press prints published on government sites (" + AGENCY
     + ", and the Parliament of Ghana at www.parliament.gh), retrieved 2026-11-27: same terms as above\n"
     "(Copyright Act, 2005 (Act 690), section 3). None of these bodies endorses this repository.\n<!-- acts:end -->"),
])
edit("REPRODUCE.md", [
    ("| WIPO Lex (secondary copies): Acts 29, 660, 667, 798, 851, 1050 |",
     "| Government agency sites (WordPress media search, one request per host at a time, 1.2 s apart): Acts 478, 497 "
     "and 1017 (Library PDFs read with `wipo_read.py`), 504, 689, 741, 749, 773, 864, 865, 891, 921, 930, and Act 896 "
     "as amended up to Act 973 | bog.gov.gh, gra.gov.gh, gipa.gov.gh, gis.gov.gh, mlnr.gov.gh, energymin.gov.gh, "
     "www.parliament.gh | 2026-11-27 | Government sites; no licence stated. Found by `tools/secondary/gov_media.py`, "
     "checked by `tools/secondary/gov_triage.py`, built by `tools/secondary/append_gov.py` (job lists from "
     "`make_job_gov.py`; reader `marg_read.py` now also takes \"ENACTED by the President and Parliament\" and drops "
     "running heads split over two lines). |\n| WIPO Lex (secondary copies): Acts 29, 660, 667, 798, 851, 1050 |"),
])
print("ok")
