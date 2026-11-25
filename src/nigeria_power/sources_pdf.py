"""Pull figures out of NERC reports and the off-grid studies.

Every number is captured from a phrase that has to be present in the PDF.
If a phrase is missing the run stops, rather than falling back to a typed value.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from nigeria_power.config import LIT_DIR, NERC_DIR, PROCESSED
from nigeria_power.pdfutil import parse_number, pdf_text, require_phrase


NERC_PAGE = "https://nerc.gov.ng/resource-category/nerc-reports/"


def _gwh(path: Path, pattern: str, label: str) -> float:
    match = require_phrase(path, pattern, label)
    return parse_number(match.group(1))


def nerc_table() -> pd.DataFrame:
    annual_2024 = NERC_DIR / "2024-Annual-Report-1.pdf"
    annual_2025 = NERC_DIR / "2025-Annual-Report_Pub.pdf"
    q1_2023 = NERC_DIR / "2023 Q1 Report_28072023_Final-2.pdf"
    q3_2023 = NERC_DIR / "NERCThirdQuarter2023Report.pdf"
    q4_2023 = NERC_DIR / "2023_Q4_Report_Final.pdf"
    q4_2024 = NERC_DIR / "2024_Q4-Report.pdf"
    q1_2025 = NERC_DIR / "2025_Q1_Report.pdf"
    q2_2025 = NERC_DIR / "2025_Q2-Report.pdf"
    q3_2025 = NERC_DIR / "2025_Q3-Report.pdf"
    q4_2025 = NERC_DIR / "2025_Q4-Report.pdf"

    rows: list[dict] = []

    def add(**kwargs) -> None:
        rows.append(kwargs)

    gen_2024 = _gwh(
        annual_2024,
        r"total generation during the year was ([\d,]+\.\d+)\s*GWh",
        "2024 annual generation",
    )
    hydro_2024 = _gwh(
        annual_2024,
        r"Hydropower plants contributed ([\d,]+\.\d+)\s*GWh",
        "2024 hydro generation",
    )
    avail_2024 = _gwh(
        annual_2024,
        r"available generation capacity of the grid-connected power plants was ([\d,]+\.\d+)\s*MW",
        "2024 available capacity",
    )
    factor_2024 = _gwh(
        annual_2024,
        r"overall availability factor for all grid-\s*connected plants was ([\d.]+)\s*%",
        "2024 availability factor",
    )
    add(
        year=2024,
        quarter=None,
        metric="grid_generation_gwh",
        value_gwh=gen_2024,
        value_twh=gen_2024 / 1000,
        boundary="Grid-connected plants, NESI. Annual total published by NERC.",
        file=annual_2024.name,
        url="https://nerc.gov.ng/wp-content/uploads/2025/07/2024-Annual-Report-1.pdf",
    )
    add(
        year=2024,
        quarter=None,
        metric="hydro_generation_gwh",
        value_gwh=hydro_2024,
        value_twh=hydro_2024 / 1000,
        boundary="Hydropower share of the same grid total.",
        file=annual_2024.name,
        url="https://nerc.gov.ng/wp-content/uploads/2025/07/2024-Annual-Report-1.pdf",
    )
    add(
        year=2024,
        quarter=None,
        metric="average_available_capacity_mw",
        value_gwh=avail_2024,
        value_twh=None,
        boundary="Average available capacity of grid-connected plants, not nameplate.",
        file=annual_2024.name,
        url="https://nerc.gov.ng/wp-content/uploads/2025/07/2024-Annual-Report-1.pdf",
    )
    add(
        year=2024,
        quarter=None,
        metric="availability_factor_percent",
        value_gwh=factor_2024,
        value_twh=None,
        boundary="NERC availability factor. Implied nameplate = available / factor.",
        file=annual_2024.name,
        url="https://nerc.gov.ng/wp-content/uploads/2025/07/2024-Annual-Report-1.pdf",
    )

    gen_2025 = _gwh(
        annual_2025,
        r"total generation during the year was ([\d,]+\.\d+)\s*GWh",
        "2025 annual generation",
    )
    hydro_2025 = _gwh(
        annual_2025,
        r"Hydropower plants contributed ([\d,]+\.\d+)\s*GWh",
        "2025 hydro generation",
    )
    avail_2025 = _gwh(
        annual_2025,
        r"average available generation capacity of the grid-connected power plants was ([\d,]+\.\d+)\s*MW",
        "2025 available capacity",
    )
    factor_2025 = _gwh(
        annual_2025,
        r"availability factor for all grid-\s*connected plants was ([\d.]+)\s*%",
        "2025 availability factor",
    )
    add(
        year=2025,
        quarter=None,
        metric="grid_generation_gwh",
        value_gwh=gen_2025,
        value_twh=gen_2025 / 1000,
        boundary="Grid-connected plants, NESI. Annual total published by NERC.",
        file=annual_2025.name,
        url="https://nerc.gov.ng/wp-content/uploads/2026/08/2025-Annual-Report_Pub.pdf",
    )
    add(
        year=2025,
        quarter=None,
        metric="hydro_generation_gwh",
        value_gwh=hydro_2025,
        value_twh=hydro_2025 / 1000,
        boundary="Hydropower share of the same grid total.",
        file=annual_2025.name,
        url="https://nerc.gov.ng/wp-content/uploads/2026/08/2025-Annual-Report_Pub.pdf",
    )
    add(
        year=2025,
        quarter=None,
        metric="average_available_capacity_mw",
        value_gwh=avail_2025,
        value_twh=None,
        boundary="Average available capacity of grid-connected plants, not nameplate.",
        file=annual_2025.name,
        url="https://nerc.gov.ng/wp-content/uploads/2026/08/2025-Annual-Report_Pub.pdf",
    )
    add(
        year=2025,
        quarter=None,
        metric="availability_factor_percent",
        value_gwh=factor_2025,
        value_twh=None,
        boundary="NERC availability factor. Implied nameplate = available / factor.",
        file=annual_2025.name,
        url="https://nerc.gov.ng/wp-content/uploads/2026/08/2025-Annual-Report_Pub.pdf",
    )

    quarters = [
        (2023, 1, q1_2023, r"generation in 2023/Q1 was ([\d,]+\.\d+)\s*GWh",
         "https://nerc.gov.ng/wp-content/uploads/2023/08/2023%20Q1%20Report_28072023_Final-2.pdf"),
        (2023, 2, q3_2023, r"from the ([\d,]+\.\d+)\s*GWh generated in 2023/Q2",
         "https://nerc.gov.ng/wp-content/uploads/2024/02/NERCThirdQuarter2023Report.pdf"),
        (2023, 3, q3_2023, r"generated in 2023/Q2 to ([\d,]+\.\d+)\s*GWh",
         "https://nerc.gov.ng/wp-content/uploads/2024/02/NERCThirdQuarter2023Report.pdf"),
        (2023, 4, q4_2023, r"2023/Q3 to ([\d,]+\.\d+)\s*GWh",
         "https://nerc.gov.ng/wp-content/uploads/2024/04/2023_Q4_Report_Final.pdf"),
        (2024, 4, q4_2024, r"translates to a total generation of ([\d,]+\.\d+)\s*GWh",
         "https://nerc.gov.ng/wp-content/uploads/2025/03/2024_Q4-Report.pdf"),
        (2025, 1, q1_2025, r"translates to a total generation of ([\d,]+\.\d+)\s*GWh",
         "https://nerc.gov.ng/wp-content/uploads/2025/07/2025_Q1_Report.pdf"),
        (2025, 2, q2_2025, r"translates to a total generation of ([\d,]+\.\d+)\s*GWh",
         "https://nerc.gov.ng/wp-content/uploads/2025/10/2025_Q2-Report.pdf"),
        (2025, 3, q4_2025, r"from ([\d,]+\.\d+)\s*GWh in 2025/Q3",
         "https://nerc.gov.ng/wp-content/uploads/2026/04/2025_Q4-Report.pdf"),
        (2025, 4, q4_2025, r"translates to a total generation of ([\d,]+\.\d+)\s*GWh",
         "https://nerc.gov.ng/wp-content/uploads/2026/04/2025_Q4-Report.pdf"),
    ]
    for year, quarter, path, pattern, url in quarters:
        value = _gwh(path, pattern, f"{year} Q{quarter}")
        note = "Quarterly grid generation published by NERC."
        if year == 2023 and quarter == 2:
            note = (
                "Figure stated in the 2023 Q3 report as the preceding quarter. "
                "The Q2 PDF text layer could not be read reliably on its own."
            )
        if year == 2025 and quarter == 3:
            note = "Figure stated in the 2025 Q4 report as the preceding quarter."
        add(
            year=year,
            quarter=quarter,
            metric="grid_generation_gwh",
            value_gwh=value,
            value_twh=value / 1000,
            boundary=note,
            file=path.name,
            url=url,
        )

    # 2023 Q3 is also repeated in the Q4 report. Keep the run honest if they diverge.
    q3_again = _gwh(q4_2023, r"from ([\d,]+\.\d+)\s*GWh in\s*2023/Q3", "2023 Q3 cross-check")
    q3_own = next(r["value_gwh"] for r in rows if r["year"] == 2023 and r["quarter"] == 3)
    if abs(q3_again - q3_own) > 0.05:
        raise RuntimeError(
            f"NERC 2023 Q3 disagrees across reports: {q3_own} vs {q3_again} GWh."
        )

    frame = pd.DataFrame(rows)
    PROCESSED.mkdir(parents=True, exist_ok=True)
    frame.to_csv(PROCESSED / "nerc_generation.csv", index=False)
    return frame


def offgrid_table() -> pd.DataFrame:
    iea = LIT_DIR / "iea_africa_energy_outlook_2019.pdf"
    wb = LIT_DIR / "worldbank_diesel_genset_nigeria_2014.pdf"
    ifc_sum = LIT_DIR / "ifc_dirty_footprint_summary_2019.pdf"
    ifc_full = LIT_DIR / "ifc_dirty_footprint_full_2019.pdf"

    require_phrase(
        iea,
        r"Nigeria accounted for almost half\s*,\s*generating 18 TWh of power from about 9 GW",
        "IEA Nigeria backup generation",
    )
    require_phrase(
        iea,
        r"40 TWh of power was generated from 40 GW of back\s*-?\s*up generating capacity in sub-\s*Saharan Africa in 2018",
        "IEA sub-Saharan backup total",
    )
    require_phrase(wb, r"total self\s*-?\s*generation at 16,360\s*GWh in 2009", "World Bank 16,360 GWh")
    require_phrase(
        wb,
        r"sectors analyzed in this study is estimated between 5,240 GWh and 20,380 GWh",
        "World Bank range",
    )
    require_phrase(
        wb,
        r"estimated generation from diesel gensets could be between 3,262 GWh and 3,423 GWh",
        "World Bank diesel range",
    )
    require_phrase(
        wb,
        r"it is not accurate to compare or aggregate results across sectors",
        "World Bank aggregation warning",
    )
    # The summary uses a dash that text extraction sometimes splits.
    require_phrase(
        ifc_sum,
        r"installed capacity of generators is between 15\s*[-–]\s*20 GW, while grid capacity is only 5\s*[-–]\s*15 GW",
        "IFC Nigeria capacity range",
    )
    require_phrase(
        ifc_full,
        r"totaling 13 GW overall",
        "IFC adjusted Nigeria fleet",
    )
    require_phrase(
        ifc_full,
        r"2\.8 million residential and 210 thousand commercial",
        "IFC site counts",
    )
    require_phrase(
        ifc_full,
        r"Nigeria, India, Iraq, Pakistan, and Venezuela account for 16 percent",
        "IFC Nigeria share of backup service",
    )
    require_phrase(
        ifc_full,
        r"In western Africa, generators account for over 40 percent of the electricity consumed annually",
        "IFC West Africa consumption share",
    )

    rows = [
        {
            "source": "IEA, Africa Energy Outlook 2019",
            "year_described": 2018,
            "metric": "backup_generation_twh",
            "low": 18.0,
            "central": 18.0,
            "high": 18.0,
            "unit": "TWh",
            "what_it_is": (
                "Modelled output of oil-fired back-up generators in Nigeria. "
                "About 9 GW of back-up capacity. Sub-Saharan Africa as a whole "
                "is given as 40 TWh from 40 GW, equal to 8% of electricity generation."
            ),
            "do_not": "Do not add this 2018 model result to a 2024 grid total.",
            "file": iea.name,
            "url": "https://www.iea.org/reports/africa-energy-outlook-2019",
            "download_url": (
                "https://iea.blob.core.windows.net/assets/"
                "2f7b6170-d616-4dd7-a7ca-a65a3a332fc1/Africa_Energy_Outlook_2019.pdf"
            ),
        },
        {
            "source": "World Bank, Diesel Power Generation study (2014), citing the Nigeria low-carbon study",
            "year_described": 2009,
            "metric": "self_generation_twh",
            "low": 16.36,
            "central": 16.36,
            "high": 16.36,
            "unit": "TWh",
            "what_it_is": "16,360 GWh of self-generation in 2009, covering diesel, gas and gasoline generators.",
            "do_not": "This is a cited earlier study, not a new measurement in the 2014 inventory.",
            "file": wb.name,
            "url": "https://documents1.worldbank.org/curated/en/853381501178909924/pdf/117772-WP-PUBLIC-52p-Report-DG-Set-Study-Nigeria.pdf",
            "download_url": "https://documents1.worldbank.org/curated/en/853381501178909924/pdf/117772-WP-PUBLIC-52p-Report-DG-Set-Study-Nigeria.pdf",
        },
        {
            "source": "World Bank, Diesel Power Generation study (2014)",
            "year_described": "2007-2012",
            "metric": "self_generation_twh",
            "low": 5.24,
            "central": None,
            "high": 20.38,
            "unit": "TWh",
            "what_it_is": (
                "Authors' own cross-sector range, 5,240 to 20,380 GWh. "
                "Sectors are for different years. The width is mostly the commercial-sector method. "
                "They warn that aggregating across sectors is not accurate and was done only for scale."
            ),
            "do_not": "Do not replace the range with its midpoint.",
            "file": wb.name,
            "url": "https://documents1.worldbank.org/curated/en/853381501178909924/pdf/117772-WP-PUBLIC-52p-Report-DG-Set-Study-Nigeria.pdf",
            "download_url": "https://documents1.worldbank.org/curated/en/853381501178909924/pdf/117772-WP-PUBLIC-52p-Report-DG-Set-Study-Nigeria.pdf",
        },
        {
            "source": "World Bank, Diesel Power Generation study (2014)",
            "year_described": "2007-2012",
            "metric": "diesel_genset_generation_twh",
            "low": 3.262,
            "central": None,
            "high": 3.423,
            "unit": "TWh",
            "what_it_is": (
                "Diesel gensets only, 3,262 to 3,423 GWh, across telecoms, manufacturing, "
                "oil and gas, residential and commercial. Gasoline generators are largely outside this total."
            ),
            "do_not": "This is not total captive generation. Gasoline sets are a large part of household use.",
            "file": wb.name,
            "url": "https://documents1.worldbank.org/curated/en/853381501178909924/pdf/117772-WP-PUBLIC-52p-Report-DG-Set-Study-Nigeria.pdf",
            "download_url": "https://documents1.worldbank.org/curated/en/853381501178909924/pdf/117772-WP-PUBLIC-52p-Report-DG-Set-Study-Nigeria.pdf",
        },
        {
            "source": "IFC, The Dirty Footprint of the Broken Grid (2019), summary",
            "year_described": 2019,
            "metric": "backup_capacity_gw",
            "low": 15.0,
            "central": None,
            "high": 20.0,
            "unit": "GW",
            "what_it_is": (
                "Conservative estimate of installed back-up generator capacity in Nigeria, "
                "15-20 GW, against grid capacity of 5-15 GW in the same sentence."
            ),
            "do_not": "Capacity, not annual energy. Do not convert to TWh without a capacity factor the study states.",
            "file": ifc_sum.name,
            "url": "https://www.ifc.org/content/dam/ifc/doc/mgrt/20190919-summary-the-dirty-footprint-of-the-broken-grid.pdf",
            "download_url": "https://www.ifc.org/content/dam/ifc/doc/mgrt/20190919-summary-the-dirty-footprint-of-the-broken-grid.pdf",
        },
        {
            "source": "IFC, The Dirty Footprint of the Broken Grid (2019), full report",
            "year_described": 2019,
            "metric": "backup_capacity_gw_adjusted",
            "low": 13.0,
            "central": 13.0,
            "high": 13.0,
            "unit": "GW",
            "what_it_is": (
                "Survey-adjusted fleet: 2.8 million residential and 210 thousand commercial sites, "
                "13 GW, described as twice the installed capacity of power plants on the grid, "
                "and $5.4 billion a year of fuel spend. Nigeria is also given as 16% of "
                "back-up energy service among the low- and middle-income countries in the model. "
                "The report does not print a Nigeria TWh next to that share, so none is derived here."
            ),
            "do_not": "Do not multiply the 16% share by the regional TWh and present the product as IFC's Nigeria total.",
            "file": ifc_full.name,
            "url": "https://www.ifc.org/content/dam/ifc/doc/mgrt/20190919-full-report-the-dirty-footprint-of-the-broken-grid.pdf",
            "download_url": "https://www.ifc.org/content/dam/ifc/doc/mgrt/20190919-full-report-the-dirty-footprint-of-the-broken-grid.pdf",
        },
    ]
    frame = pd.DataFrame(rows)
    frame.to_csv(PROCESSED / "offgrid_estimates.csv", index=False)
    return frame


def confirm_ember_methodology() -> dict[str, bool]:
    path = Path(__file__).resolve().parents[2] / "data" / "raw" / "ember" / "ember_electricity_data_methodology.pdf"
    text = pdf_text(str(path))
    checks = {
        "annual_from_eia": "Annual electricity generation and net imports are taken from the EIA." in text,
        "monthly_from_tcn": "Monthly generation is taken from TCN." in text,
        "thermal_assumed_gas": "All thermal power generation is assumed to be Gas." in text,
        "distributed_solar_not_in_monthly": (
            "Distributed generation, including Solar, is not captured in monthly data." in text
        ),
        "summing_months_will_not_match": (
            "simply summing up monthly values will not produce the same results as our annual values" in text
        ),
        "nigeria_heading": "Nigeria" in text,
    }
    missing = [key for key, ok in checks.items() if not ok]
    if missing:
        raise RuntimeError(f"Ember methodology PDF is missing expected statements: {missing}")
    return checks
