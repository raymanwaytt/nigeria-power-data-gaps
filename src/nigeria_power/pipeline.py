"""Download (optional) -> slice -> read PDFs -> compare -> chart."""

from __future__ import annotations

import json
from pathlib import Path

from nigeria_power.analyse import (
    build_findings,
    fuel_comparison,
    load_frames,
    monthly_vs_annual,
    nigeria_annual,
    west_africa,
    world_bank_access,
)
from nigeria_power.charts import make_charts
from nigeria_power.config import CACHE, OUTPUTS, PROCESSED, SLICES
from nigeria_power.download import download_sources, write_slices
from nigeria_power.sources_pdf import confirm_ember_methodology, nerc_table, offgrid_table


def main(download: bool = False) -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    if download or not (SLICES / "ember_yearly_ecowas.csv").exists():
        if download or not (CACHE / "ember_yearly_global.csv").exists():
            download_sources()
        write_slices()
    elif (CACHE / "ember_yearly_global.csv").exists() and download:
        write_slices()

    print("Reading NERC reports and off-grid studies…")
    confirm_ember_methodology()
    nerc = nerc_table()
    offgrid = offgrid_table()
    frames = load_frames()
    annual = nigeria_annual(frames, nerc)
    fuels = fuel_comparison(frames)
    monthly = monthly_vs_annual(frames)
    west = west_africa(frames)
    access = world_bank_access()
    findings = build_findings(annual, fuels, monthly, west, nerc, access)
    _checks(annual, fuels, findings)
    make_charts(annual, fuels, monthly, west, offgrid)
    print(json.dumps({k: findings[k] for k in (
        "first_year_ember_eia_gap_above_0_05_twh",
        "year_2024",
        "year_2025",
        "solar",
        "nerc_2025_annual_minus_quarters_gwh",
        "hydro_2024",
        "access_to_electricity",
    )}, indent=2))
    print("Charts written to outputs/figures/")


def _checks(annual, fuels, findings) -> None:
    solar_2025 = fuels[(fuels["year"] == 2025) & (fuels["fuel"] == "Solar")].iloc[0]
    if solar_2025["ember_capacity_factor"] <= 1:
        raise RuntimeError("Expected Nigeria 2025 solar capacity factor above 100%.")
    if abs(findings["max_abs_ember_identity_gap_twh"]) > 0.02:
        raise RuntimeError("Ember demand identity failed.")
    if abs(findings["max_abs_eia_identity_gap_twh"]) > 0.05:
        raise RuntimeError("EIA generation/consumption identity failed.")
    y2010 = annual.loc[annual["year"] == 2010].iloc[0]
    if abs(y2010["ember_minus_eia_twh"]) > 0.02:
        raise RuntimeError("2010 Ember and EIA were expected to match within rounding.")
    # Keep a human-readable one-page table next to the charts.
    keep = annual[annual["year"].between(2015, 2025)][
        [
            "year",
            "ember_generation_twh",
            "eia_generation_twh",
            "owid_generation_twh",
            "nerc_generation_twh",
            "ember_minus_eia_twh",
        ]
    ]
    keep.to_csv(PROCESSED / "nigeria_recent_years.csv", index=False)
    Path(OUTPUTS / "findings.json").write_text(
        Path(PROCESSED / "findings.json").read_text()
    )
