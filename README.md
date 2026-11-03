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

<!-- acts:start -->
## Acts of Parliament from the Parliament of Ghana

140 Acts of Parliament as passed (1960 to 2021), 4,801 files, one folder per Act named by its number (`act-0651/` is the Labour Act, 2003 (Act 651)). Each is one version, the Act as passed, dated by the date of assent printed on it; where an Act comes into force later (a commencement section, an Executive Instrument), that later day is not shown. Later amending Acts are their own folders; their changes are not replayed into the Acts they amend.

**Source.** The Parliament of Ghana Library publishes typed editions of the Acts (PDFs made from Microsoft Word, with a text layer) in its repository, [repository.parliament.gh](https://repository.parliament.gh/). Each Act here is read from that edition; no OCR. The Library's consolidated editions, marked "As amended by", are not used, and nor are the scanned prints, which have no usable text layer.

**How it was checked.** Every word from "AN ACT" to the Gazette notification line is in a file, checked letter for letter, except page numbers, footnote markers and the Part and group headings printed above sections; each section's title is its file's first line. An Act whose sections are not numbered 1, 2, 3 and so on without a gap is left out. The typed edition is a re-keyed text, not a facsimile of the Assembly Press print: read the same way, the Library's edition of the Cybersecurity Act, 2020 has the same words as the Assembly Press print in `cybersecurity/` in 62 of its 103 provisions, and the others differ by a punctuation mark, a paragraph letter or a typing slip (each at least 97.5% the same, letter for letter).

| Folder | Act | Assent |
| --- | --- | --- |
| `act-0002/` | [Land Development (Protection of Purchases) Act, 1960 (Act 2)](https://repository.parliament.gh/handle/123456789/1877) | 1960-08-09 |
| `act-0011/` | [International Development Association Act, 1960 (Act 11)](https://repository.parliament.gh/handle/123456789/1894) | 1960-12-08 |
| `act-0026/` | [Notaries Public Act, 1960 (Act 26)](https://repository.parliament.gh/handle/123456789/2001) | 1960-12-22 |
| `act-0075/` | [Foreign Enlistment Act, 1961 (Act 75)](https://repository.parliament.gh/handle/123456789/1833) | 1961-08-17 |
| `act-0083/` | [Diseases of Animals Act, 1961 (Act 83)](https://repository.parliament.gh/handle/123456789/1804) | 1961-11-01 |
| `act-0107/` | [Farm Lands (Protection) Act, 1962 (Act 107)](https://repository.parliament.gh/handle/123456789/1826) | 1962-02-24 |
| `act-0122/` | [Lands Registry Act, 1962 (Act 122)](https://repository.parliament.gh/handle/123456789/1886) | 1962-06-14 |
| `act-0148/` | [Diplomatic Immunities Act, 1962 (Act 148)](https://repository.parliament.gh/handle/123456789/1803) | 1962-11-07 |
| `act-0156/` | [Wholesale Fish Marketing Act, 1963 (Act 156)](https://repository.parliament.gh/handle/123456789/2053) | 1963-01-03 |
| `act-0170/` | [Chartered Accountants Act, 1963 (Act 170)](https://repository.parliament.gh/handle/123456789/1768) | 1963-04-19 |
| `act-0176/` | [Civil Liability Act, 1963 (Act 176)](https://repository.parliament.gh/handle/123456789/1775) | 1963-04-19 |
| `act-0186/` | [Lands (Statutory Way Leaves) Act, 1963 (Act 186)](https://repository.parliament.gh/handle/123456789/1892) | 1963-07-16 |
| `act-0244/` | [Habeas Corpus Act, 1964 (Act 244)](https://repository.parliament.gh/handle/123456789/1857) | 1964-05-26 |
| `act-0271/` | [Estate Duty Act, 1965 (Act 271)](https://repository.parliament.gh/handle/123456789/1820) | 1965-03-23 |
| `act-0280/` | [Anatomy Act, 1965 (Act 280)](https://repository.parliament.gh/handle/123456789/2047) | 1965-04-09 |
| `act-0302/` | [Public Conveyancing Act, 1965 (Act 302)](https://repository.parliament.gh/handle/123456789/1934) | 1965-09-29 |
| `act-0313/` | [Africa Defence (Ghana) Act, 1965 (Act 313)](https://repository.parliament.gh/handle/123456789/1747) | 1965-11-26 |
| `act-0426/` | [Ghana National Service Scheme Act, 1980 (Act 426)](https://repository.parliament.gh/handle/123456789/1854) | 1980-09-23 |
| `act-0452/` | [National Commission for Civic Education Act, 1993 (Act 452)](https://repository.parliament.gh/handle/123456789/1902) | 1993-07-06 |
| `act-0472/` | [Emergency Powers Act, 1994 (Act 472)](https://repository.parliament.gh/handle/123456789/1814) | 1994-02-14 |
| `act-0479/` | [National Development Planning Commission Act, 1994 (Act 479)](https://repository.parliament.gh/handle/123456789/1972) | 1994-08-29 |
| `act-0490/` | [Environmental Protection Agency Act, 1994 (Act 490)](https://repository.parliament.gh/handle/123456789/1819) | 1994-12-30 |
| `act-0491/` | [Public Order Act, 1994 (Act 491)](https://repository.parliament.gh/handle/123456789/2040) | 1994-12-30 |
| `act-0528/` | [Pesticides Control and Management Act, 1996 (Act 528)](https://repository.parliament.gh/handle/123456789/1909) | 1996-12-23 |
| `act-0537/` | [The Ghana National Fire Service Act, 1997 (Act 537)](https://repository.parliament.gh/handle/123456789/2105) | 1997-08-29 |
| `act-0540/` | [Ghana Highway Authority Act, 1997 (Act 540)](https://repository.parliament.gh/handle/123456789/1848) | 1997-12-31 |
| `act-0549/` | [Powers of Attorney Act, 1998 (Act 549)](https://repository.parliament.gh/handle/123456789/1938) | 1998-04-27 |
| `act-0572/` | [Fines(Penalty Units)Act, 2000 (Act 572)](https://repository.parliament.gh/handle/123456789/1830) | 2000-02-02 |
| `act-0573/` | [Immigration Act, 2000 (Act 573)](https://repository.parliament.gh/handle/123456789/1860) | 2000-02-02 |
| `act-0582/` | [Export Development and Investment Fund Act, 2000 (Act 582)](https://repository.parliament.gh/handle/123456789/1823) | 2000-10-04 |
| `act-0588/` | [Atomic Energy Commission Act, 2000 (Act 588)](https://repository.parliament.gh/handle/123456789/1759) | 2000-11-27 |
| `act-0589/` | [Protection against Unfair Competition Act, 2000 (Act 589)](https://repository.parliament.gh/handle/123456789/1935) | 2000-12-19 |
| `act-0591/` | [Citizen Act, 2000 (Act 591)](https://repository.parliament.gh/handle/123456789/1773) | 2000-12-29 |
| `act-0611/` | [National Reconciliation Commission Act, 2002 (Act 611)](https://repository.parliament.gh/handle/123456789/1924) | 2002-01-09 |
| `act-0625/` | [Fisheries Act, 2002 (Act 625)](https://repository.parliament.gh/handle/123456789/1832) | 2002-01-16 |
| `act-0612/` | [Bank of Ghana Act, 2002 (Act 612)](https://repository.parliament.gh/handle/123456789/1761) | 2002-01-24 |
| `act-0616/` | [Ghana Investment Fund Act, 2002 (Act 616)](https://repository.parliament.gh/handle/123456789/1851) | 2002-04-08 |
| `act-0630/` | [Ghana Maritime Authority Act, 2002 (Act 630)](https://repository.parliament.gh/handle/123456789/1853) | 2002-07-25 |
| `act-0647/` | [Institute of Local Government Studies Act, 2003 (Act 647)](https://repository.parliament.gh/handle/123456789/1872) | 2003-07-03 |
| `act-0649/` | [Postal and Courier Services Regulatory Commission Act, 2003 (Act 649)](https://repository.parliament.gh/handle/123456789/1940) | 2003-08-10 |
| `act-0651/` | [Labour Act, 2003 (Act 651)](https://repository.parliament.gh/handle/123456789/1874) | 2003-10-08 |
| `act-0652/` | [Kimberley Process Certificate Act, 2003 (Act 652)](https://repository.parliament.gh/handle/123456789/1890) | 2003-10-24 |
| `act-0653/` | [Juvenile Justice Act, 2003 (Act 653)](https://repository.parliament.gh/handle/123456789/1891) | 2003-10-28 |
| `act-0657/` | [Patents Act, 2003 (Act 657)](https://repository.parliament.gh/handle/123456789/1914) | 2003-12-31 |
| `act-0659/` | [Geographical Indications Act, 2003 (Act 659)](https://repository.parliament.gh/handle/123456789/1839) | 2003-12-31 |
| `act-0664/` | [Trade Marks Act, 2004 (Act 664)](https://repository.parliament.gh/handle/123456789/2140) | 2004-01-29 |
| `act-0675/` | [Ghana Maritime Security Act, 2004 (Act 675)](https://repository.parliament.gh/handle/123456789/1841) | 2004-11-01 |
| `act-0676/` | [Ghana Institute of Management and Public Administration Act, 2004 (Act 676)](https://repository.parliament.gh/handle/123456789/1849) | 2004-11-11 |
| `act-0684/` | [Internal Revenue (Registration of Business) Act, 2005 (Act 684)](https://repository.parliament.gh/handle/123456789/1896) | 2005-01-06 |
| `act-0690/` | [Copyright Act, 2005 (Act 690)](https://repository.parliament.gh/handle/123456789/1785) | 2005-05-17 |
| `act-0691/` | [National Petroleum Authority Act, 2005 (Act 691)](https://repository.parliament.gh/handle/123456789/1926) | 2005-06-14 |
| `act-0694/` | [Human Trafficking Act, 2005 (Act 694)](https://repository.parliament.gh/handle/123456789/1859) | 2005-12-05 |
| `act-0701/` | [The Ghana National Commission on Children ( Repeal) Act, 2006 (Act 701)](https://repository.parliament.gh/handle/123456789/2104) | 2006-03-23 |
| `act-0706/` | [Subvented Agencies Act, 2006 (Act 706)](https://repository.parliament.gh/handle/123456789/2082) | 2006-04-06 |
| `act-0708/` | [Insolvency Act, 2006 (Act 708)](https://repository.parliament.gh/handle/123456789/1870) | 2006-04-18 |
| `act-0716/` | [Auction Sales Act, 2006 (Act 716)](https://repository.parliament.gh/handle/123456789/1760) | 2006-08-14 |
| `act-0717/` | [Institute of Journalism Act, 2006 (Act 717)](https://repository.parliament.gh/handle/123456789/1871) | 2006-08-31 |
| `act-0718/` | [Council for Technical and Vocational Education and Training Act, 2006 (Act 718)](https://repository.parliament.gh/handle/123456789/1790) | 2006-08-31 |
| `act-0719/` | [The West African Examination Council Act, 2006 (Act 719)](https://repository.parliament.gh/handle/123456789/2110) | 2006-08-31 |
| `act-0720/` | [Whistleblower Act, Act, 2006 (Act 720)](https://repository.parliament.gh/handle/123456789/2054) | 2006-10-16 |
| `act-0721/` | [Gaming Act, 2006 (Act 721)](https://repository.parliament.gh/handle/123456789/1838) | 2006-12-22 |
| `act-0724/` | [Insurance Act, 2006 (Act 724)](https://repository.parliament.gh/handle/123456789/1873) | 2006-12-29 |
| `act-0725/` | [Appropriation Act, 2006 (Act 725)](https://repository.parliament.gh/handle/123456789/2045) | 2006-12-29 |
| `act-0728/` | [National Reconstruction Levy (Repeal) Act, 2007 (Act 728)](https://repository.parliament.gh/handle/123456789/2007) | 2007-04-05 |
| `act-0733/` | [Central Securities Depository Act, 2007 (Act 733)](https://repository.parliament.gh/handle/123456789/1767) | 2007-05-16 |
| `act-0735/` | [Ministries, Departments and Agencies (Retention of Funds) Act, 2007 (Act 735)](https://repository.parliament.gh/handle/123456789/1923) | 2007-05-18 |
| `act-0737/` | [Fair Wages and Salaries Commission Act, 2007 (Act 737)](https://repository.parliament.gh/handle/123456789/1825) | 2007-06-04 |
| `act-0743/` | [Transfer of Convicted Persons Act, 2007 (Act 743)](https://repository.parliament.gh/handle/123456789/2138) | 2007-08-20 |
| `act-0746/` | [The restriction on use of military uniforms and equipment (Amendment) Act, 2008 (Act 746)](https://repository.parliament.gh/handle/123456789/2107) | 2008-01-04 |
| `act-0757/` | [Internal Revenue (Amendment) Act, 2008 (Act 757)](https://repository.parliament.gh/handle/123456789/1899) | 2008-06-16 |
| `act-0759/` | [Chieftaincy Act, 2008 (Act 759)](https://repository.parliament.gh/handle/123456789/1771) | 2008-06-16 |
| `act-0760/` | [Financial Administration (Amendment) Act, 2008 (Act 760)](https://repository.parliament.gh/handle/123456789/1828) | 2008-07-02 |
| `act-0761/` | [Road Traffic (Amendment) Act, 2008 (Act 761)](https://repository.parliament.gh/handle/123456789/2069) | 2008-09-29 |
| `act-0766/` | [National Pensions Act, 2008 (Act 766)](https://repository.parliament.gh/handle/123456789/1927) | 2008-12-04 |
| `act-0767/` | [Lands Commission Act, 2008 (Act 767)](https://repository.parliament.gh/handle/123456789/1888) | 2008-12-04 |
| `act-0769/` | [National Communications Authority Act, 2008 (Act 769)](https://repository.parliament.gh/handle/123456789/1901) | 2008-12-11 |
| `act-0771/` | [National Information Technology Agency Act, 2008 (Act 771)](https://repository.parliament.gh/handle/123456789/1931) | 2008-12-11 |
| `act-0774/` | [Non - Bank Financial Institution Act, 2008 (Act 774)](https://repository.parliament.gh/handle/123456789/2003) | 2008-12-23 |
| `act-0902/` | [Income Tax (Amendment) Act, 2015 (Act 902)](https://repository.parliament.gh/handle/123456789/1865) | 2015-12-30 |
| `act-0907/` | [Income Tax (Amendment) Act, 2016 (Act 907)](https://repository.parliament.gh/handle/123456789/1866) | 2016-02-18 |
| `act-0908/` | [Immigration Service Act, 2016 (Act 908)](https://repository.parliament.gh/handle/123456789/1861) | 2016-03-08 |
| `act-0919/` | [Petroleum (Exploration and Production) Act, 2016 (Act 919)](https://repository.parliament.gh/handle/123456789/1908) | 2016-08-19 |
| `act-0943/` | [Customs and Excise (Petroleum Taxes and Petroleum Related Levies) (Repeal) Act, 2017 (Act 943)](https://repository.parliament.gh/handle/123456789/1798) | 2017-03-15 |
| `act-0946/` | [Energy Sector Levies (Amendment) Act, 2017 (Act 946)](https://repository.parliament.gh/handle/123456789/1816) | 2017-04-05 |
| `act-0947/` | [Earmarked Funds Capping and Realignment Act, 2017 (Act 947)](https://repository.parliament.gh/handle/123456789/1808) | 2017-04-05 |
| `act-0948/` | [Value Added Tax (Amendment) Act, 2017 (Act 948)](https://repository.parliament.gh/handle/123456789/2139) | 2017-04-05 |
| `act-0952/` | [African Union Import Levy Act, 2017 (Act 952)](https://repository.parliament.gh/handle/123456789/1755) | 2017-12-29 |
| `act-0954/` | [Value Added Tax (Amendment) (No. 2) Act, 2017 (Act 954)](https://repository.parliament.gh/handle/123456789/2112) | 2017-12-29 |
| `act-0955/` | [Tax Amnesty Act, 2017 (Act 955)](https://repository.parliament.gh/handle/123456789/2099) | 2017-12-29 |
| `act-0956/` | [Income Tax (Amendment) (No. 2) Act, 2017 (Act 956)](https://repository.parliament.gh/handle/123456789/1863) | 2017-12-29 |
| `act-0957/` | [Customs (Amendment) (No.2) Act, 2017 (Act 957)](https://repository.parliament.gh/handle/123456789/1797) | 2017-12-29 |
| `act-0958/` | [National Fiscal Stability Levy (Amendment) Act, 2017 (Act 958)](https://repository.parliament.gh/handle/123456789/1942) | 2017-12-29 |
| `act-0966/` | [Taxation( Use of Fiscal Electronic Device) Act, 2018 (Act 966)](https://repository.parliament.gh/handle/123456789/2100) | 2018-05-04 |
| `act-0968/` | [Ghana Deposit Protection (Amendment) Act, 2018 (Act 968)](https://repository.parliament.gh/handle/123456789/1842) | 2018-05-04 |
| `act-0970/` | [Value Added Tax (Amendment) Act, 2018 (Act 970)](https://repository.parliament.gh/handle/123456789/2136) | 2018-07-31 |
| `act-0971/` | [National Health Insurance (Amendment) Act, 2018 (Act 971)](https://repository.parliament.gh/handle/123456789/1939) | 2018-07-31 |
| `act-0972/` | [Ghana Education Trust Fund (Amendment) Act, 2018 (Act 972)](https://repository.parliament.gh/handle/123456789/1844) | 2018-07-31 |
| `act-0973/` | [Income Tax (Amendment) Act, 2018 (Act 973)](https://repository.parliament.gh/handle/123456789/1868) | 2018-07-31 |
| `act-0974/` | [Technical Universities (Amendment) Act, 2018 (Act 974)](https://repository.parliament.gh/handle/123456789/2102) | 2018-08-24 |
| `act-0975/` | [Witness Protection Act, 2018 (Act 975)](https://repository.parliament.gh/handle/123456789/2051) | 2018-08-24 |
| `act-0977/` | [Legal Aid Commission Act, 2018 (Act 977)](https://repository.parliament.gh/handle/123456789/1881) | 2018-09-13 |
| `act-0978/` | [Minerals Income Investment Fund Act, 2018 (Act 978)](https://repository.parliament.gh/handle/123456789/1897) | 2018-12-03 |
| `act-0980/` | [Value Added Tax (Amendment) (No.2) Act, 2018 (Act 980)](https://repository.parliament.gh/handle/123456789/2113) | 2018-12-28 |
| `act-0981/` | [Excise Tax Stamp (Amendment) Act, 2018 (Act 981)](https://repository.parliament.gh/handle/123456789/1821) | 2018-12-28 |
| `act-0982/` | [Fiscal Responsibility Act, 2018 (Act 982)](https://repository.parliament.gh/handle/123456789/1831) | 2018-12-28 |
| `act-0987/` | [Payment Systems and Services Act, 2019 (Act 987)](https://repository.parliament.gh/handle/123456789/1912) | 2019-05-13 |
| `act-0988/` | [Ghana Integrated Iron and Steel Development Corporation Act, 2019 (Act 988)](https://repository.parliament.gh/handle/123456789/1850) | 2019-05-13 |
| `act-0990/` | [State Interests and Governance Authority Act, 2019 (Act 990)](https://repository.parliament.gh/handle/123456789/2072) | 2019-06-07 |
| `act-0993/` | [National Road Safety Authority Act, 2019 (Act 993)](https://repository.parliament.gh/handle/123456789/2006) | 2019-08-02 |
| `act-0996/` | [Luxury Vehicle Levy (Repeal) Act, 2019 (Act 996)](https://repository.parliament.gh/handle/123456789/1922) | 2019-08-19 |
| `act-0998/` | [Communications Service Tax (Amendment) Act, 2019 (Act 998)](https://repository.parliament.gh/handle/123456789/1779) | 2019-08-19 |
| `act-0999/` | [Vigilantism and Related Offences Act, 2019 (Act 999)](https://repository.parliament.gh/handle/123456789/2057) | 2019-08-23 |
| `act-1000/` | [C.K. TEDAM UNIVERSITY OF TECHNOLOGY AND APPLIED SCIENCES ACT, 2019 (Act 1000)](https://repository.parliament.gh/handle/123456789/1766) | 2019-08-23 |
| `act-1002/` | [Ghana Meteorological Agency (Amendment) Act, 2019 (Act 1002)](https://repository.parliament.gh/handle/123456789/1840) | 2019-09-24 |
| `act-1009/` | [Ghana Health Service and Teaching Hospitals (Amendment) Act, 2019 (Act 1009)](https://repository.parliament.gh/handle/123456789/1846) | 2019-12-27 |
| `act-1006/` | [Electronic Communications (Amendment) Act, 2019 (Act 1006)](https://repository.parliament.gh/handle/123456789/1812) | 2019-12-28 |
| `act-1010/` | [Tree Crops Development Authority Act, 2019 (Act 1010)](https://repository.parliament.gh/handle/123456789/2137) | 2019-12-28 |
| `act-1012/` | [Imposition of Restrictions Act, 2020 (Act 1012)](https://repository.parliament.gh/handle/123456789/1862) | 2020-03-21 |
| `act-1013/` | [Novel Corona Virus (Covid- 19) National Trust Fund Act, 2020 (Act 1013)](https://repository.parliament.gh/handle/123456789/2000) | 2020-04-03 |
| `act-1016/` | [Technical Universities (Amendment) Act, 2020 (Act 1016)](https://repository.parliament.gh/handle/123456789/2103) | 2020-04-30 |
| `act-1019/` | [Narcotics Control Commission Act, 2020 (Act 1019)](https://repository.parliament.gh/handle/123456789/1921) | 2020-05-11 |
| `act-1020/` | [Chartered Institute of Human Resource Management, Ghana Act, 2020 (Act 1020)](https://repository.parliament.gh/handle/123456789/1769) | 2020-08-13 |
| `act-1021/` | [Chartered Institute of Marketing, Ghana Act, 2020 (Act 1021)](https://repository.parliament.gh/handle/123456789/1770) | 2020-08-13 |
| `act-1025/` | [Communications Service Tax (Amendment) Act, 2020 (Act 1025)](https://repository.parliament.gh/handle/123456789/1780) | 2020-08-27 |
| `act-1026/` | [Akenten Appiah-Menka University of Skills Training and Entrepreneurial Development Act, 2020 (Act 1026)](https://repository.parliament.gh/handle/123456789/1757) | 2020-08-27 |
| `act-1027/` | [Registration of Births and Deaths Act, 2020 (Act 1027)](https://repository.parliament.gh/handle/123456789/2061) | 2020-10-06 |
| `act-1029/` | [Revenue Administration (Amendment) Act, 2020 (Act 1029)](https://repository.parliament.gh/handle/123456789/2064) | 2020-10-06 |
| `act-1034/` | [Criminal Offences (Amendment) Act, 2020 (Act 1034)](https://repository.parliament.gh/handle/123456789/1795) | 2020-10-27 |
| `act-1036/` | [Land Act, 2020 (Act 1036)](https://repository.parliament.gh/handle/123456789/1875) | 2020-12-23 |
| `act-1037/` | [Council of State Act, 2020 (Act 1037)](https://repository.parliament.gh/handle/123456789/1791) | 2020-12-23 |
| `act-1039/` | [Public Private Partnership Act, 2020 (Act 1039)](https://repository.parliament.gh/handle/123456789/2039) | 2020-12-29 |
| `act-1040/` | [National Signals Bureau Act, 2020 (Act 1040)](https://repository.parliament.gh/handle/123456789/2004) | 2020-12-29 |
| `act-1041/` | [National Ambulance Service Act, 2020 (Act 1041)](https://repository.parliament.gh/handle/123456789/1919) | 2020-12-29 |
| `act-1042/` | [National Blood Service Act, 2020 (Act 1042)](https://repository.parliament.gh/handle/123456789/1918) | 2020-12-29 |
| `act-1043/` | [Ghana Enterprises Agency Act, 2020 (Act 1043)](https://repository.parliament.gh/handle/123456789/1845) | 2020-12-29 |
| `act-1047/` | [Real Estate Agency Act, 2020 (Act 1047)](https://repository.parliament.gh/handle/123456789/2060) | 2020-12-29 |
| `act-1048/` | [Creative Arts Industry Act, 2020 (Act 1048)](https://repository.parliament.gh/handle/123456789/1793) | 2020-12-29 |
| `act-1053/` | [Petroleum Hub Development Corporation Act, 2020 (Act 1053)](https://repository.parliament.gh/handle/123456789/1907) | 2020-12-29 |
| `act-1064/` | [Energy Sector Levies (Amendment) Act, 2021 (Act 1064)](https://repository.parliament.gh/handle/123456789/1818) | 2021-03-31 |
| `act-1067/` | [Financial Sector Recovery Levy Act, 2021 (Act 1067)](https://repository.parliament.gh/handle/123456789/1829) | 2021-03-31 |
<!-- acts:end -->

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
