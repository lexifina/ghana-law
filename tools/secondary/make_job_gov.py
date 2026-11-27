"""Write sec/job_gov.json: Acts as passed from government-hosted prints and Library items with fixed readers."""
import os
import json, sys
sys.path.insert(0, os.path.join(os.environ.get("GH_ACQ", "."), "tools"))
import build as B
G = os.path.join(os.environ.get("GH_ACQ", "."), 'sec/cache/gov')
P = os.path.join(os.environ.get("GH_ACQ", "."), 'cache/pdf')
ASSENT = "date of assent printed on the Act (no commencement day printed in its sections)"
rows = [
    # pdf, reader, title, num, year, enacted, published, inf, basis, source page, file url, publisher
    (G + r"\gipc.gov.gh\GHANA-INVESTMENT-PROMOTION-CENTRE-GIPC-ACT-865.pdf", "marg",
     "Ghana Investment Promotion Centre Act, 2013 (Act 865)", 865, 2013, "2013-08-26", "2013-10-30", "2013-08-26", ASSENT,
     "https://gipa.gov.gh/wp-content/uploads/2023/04/GHANA-INVESTMENT-PROMOTION-CENTRE-GIPC-ACT-865.pdf",
     "the Ghana Investment Promotion Authority (gipa.gov.gh)"),
    (G + r"\bog.gov.gh\BANKS-AND-SPECIALISED-DEPOSIT-ACT-2016.pdf", "marg",
     "Banks and Specialised Deposit-Taking Institutions Act, 2016 (Act 930)", 930, 2016, "2016-09-14", "", "2016-09-14",
     ASSENT, "https://www.bog.gov.gh/wp-content/uploads/2019/09/BANKS-AND-SPECIALISED-DEPOSIT-ACT-2016.pdf",
     "the Bank of Ghana (bog.gov.gh)"),
    (G + r"\gra.gov.gh\Customs-Act-2015.pdf", "marg", "Customs Act, 2015 (Act 891)", 891, 2015, "2015-05-18",
     "2015-05-18", "2015-05-18", ASSENT, "https://gra.gov.gh/wp-content/uploads/2023/08/Customs-Act-2015.pdf",
     "the Ghana Revenue Authority (gra.gov.gh)"),
    (G + r"\gra.gov.gh\Communications-Service-Tax-Amendment.-Act-2013..pdf", "wipo",
     "Communications Service Tax (Amendment) Act, 2013 (Act 864)", 864, 2013, "2013-07-12", "2013-07-15", "2013-07-12",
     ASSENT, "https://gra.gov.gh/wp-content/uploads/2022/02/Communications-Service-Tax-Amendment.-Act-2013..pdf",
     "the Ghana Revenue Authority (gra.gov.gh)"),
    (G + r"\gra.gov.gh\Free-Zones-Act-1995-Act-504.pdf", "marg", "Free Zones Act, 1995 (Act 504)", 504, 1995,
     "1995-08-31", "", "1995-08-31", ASSENT,
     "https://gra.gov.gh/wp-content/uploads/2020/10/Free-Zones-Act-1995-Act-504.pdf",
     "the Ghana Revenue Authority (gra.gov.gh)"),
    (G + r"\mlnr.gov.gh\PUBLIC-FINANCIAL-MANAGT.-ACT-2016.pdf", "marg", "Public Financial Management Act, 2016 (Act 921)",
     921, 2016, "2016-08-25", "2016-08-26", "2016-08-25", ASSENT,
     "https://mlnr.gov.gh/wp-content/uploads/2025/07/PUBLIC-FINANCIAL-MANAGT.-ACT-2016.pdf",
     "the Ministry of Lands and Natural Resources (mlnr.gov.gh)"),
    (G + r"\gis.gov.gh\Anti-Money-Laundering-Act-2008-Act-749.pdf", "marg", "Anti-Money Laundering Act, 2008 (Act 749)",
     749, 2008, "2008-01-22", "2008-01-25", "2008-01-22", ASSENT,
     "https://gis.gov.gh/wp-content/uploads/2024/02/Anti-Money-Laundering-Act-2008-Act-749.pdf",
     "the Ghana Immigration Service (gis.gov.gh)"),
    (G + r"\bog.gov.gh\Borrowers-and-Lenders-Act-No.-773.pdf", "marg", "Borrowers and Lenders Act, 2008 (Act 773)", 773,
     2008, "2008-12-23", "2009-01-09", "2008-12-23", ASSENT,
     "https://www.bog.gov.gh/wp-content/uploads/2020/02/Borrowers-and-Lenders-Act-No.-773.pdf",
     "the Bank of Ghana (bog.gov.gh)"),
    (G + r"\gra.gov.gh\ACT689StampDutyAct.pdf", "marg", "Stamp Duty Act, 2005 (Act 689)", 689, 2005, "2005-05-17",
     "2005-06-03", "2005-01-01",
     "section 52 (\"The Act shall come into force on 1st January, 2005\"); date of assent 2005-05-17",
     "https://gra.gov.gh/wp-content/uploads/2021/05/ACT689StampDutyAct.pdf", "the Ghana Revenue Authority (gra.gov.gh)"),
    (os.path.join(os.environ.get("GH_ACQ", "."), 'sec/cache/legacy/ACT_741.pdf'), "marg", "Criminal Code (Amendment) Act, 2007 (Act 741)",
     741, 2007, "2007-08-07", "2007-08-10", "2007-08-07", ASSENT,
     "https://www.parliament.gh/epanel/docs/bills/ACT%20741.pdf", "the Parliament of Ghana (parliament.gh)"),
    (P + r"\ca8264ac-76a3-4695-a44e-d10a90076ae5.pdf", "wipo", "Income Tax (Amendment) Act, 2020 (Act 1017)", 1017, 2020,
     "2020-05-08", "", "2020-05-08",
     ASSENT + "; the Gazette date printed on this copy (30 December 2019) precedes assent and is not used",
     "https://repository.parliament.gh/handle/123456789/1869", "the Parliament of Ghana Library (repository.parliament.gh)"),
    (P + r"\d883c5b0-2d06-4e47-9ffd-425d33dfd2cd.pdf", "wipo", "Ghana Investment Promotion Centre Act, 1994 (Act 478)",
     478, 1994, "1994-08-29", "1994-09-02", "1994-08-29", ASSENT,
     "https://repository.parliament.gh/handle/123456789/1852", "the Parliament of Ghana Library (repository.parliament.gh)"),
    (P + r"\65be873c-62d5-4bab-aa9f-8ea6d597d8ca.pdf", "wipo", "Electricity (Special Levies) Act, 1995 (Act 497)", 497,
     1995, "1995-02-02", "1995-02-10", "1995-02-02", ASSENT,
     "https://repository.parliament.gh/handle/123456789/1811", "the Parliament of Ghana Library (repository.parliament.gh)"),
]
out = []
for pdf, rd, title, num, yr, en, pub, inf, basis, src, publisher in rows:
    short = title.split(" (Act")[0].replace(",", "")
    file_url = src
    if "repository.parliament.gh/handle" in src:
        file_url = f"https://repository.parliament.gh/server/api/core/bitstreams/{pdf.rsplit(chr(92), 1)[1][:-4]}/content"
    out.append(dict(pdf=pdf, reader=rd, mode="passed", folder=f"acts/{yr}/{num}-{B.slug_of(title)}", title=title,
                    short=short, law=f"Act {num}", enacted=en, published=pub, inf=inf, basis=basis, source=src,
                    source_file=file_url, publisher=publisher, text_source="publisher text layer"))
json.dump(out, open(os.path.join(os.environ.get("GH_ACQ", "."), 'sec/job_gov.json'), "w", encoding="utf8"), indent=1, ensure_ascii=False)
for o in out:
    print(o["folder"], o["inf"])
