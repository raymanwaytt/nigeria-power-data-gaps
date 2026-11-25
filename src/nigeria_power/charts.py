"""Charts for the Nigeria reconciliation. Titles state the finding."""

from __future__ import annotations

import textwrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from nigeria_power.config import FIGURES

EMBER = "#C2410C"
EIA = "#1D4E89"
OWID = "#0F766E"
NERC = "#6D28D9"
INK = "#1F2933"
MUTED = "#52606D"
GRID = "#E4E7EB"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.edgecolor": "#9AA5B1",
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.titlesize": 13,
        "axes.labelsize": 10,
    }
)


def _footnote(fig: plt.Figure, source: str) -> float:
    wrapped = textwrap.fill(source, width=148)
    lines = wrapped.count("\n") + 1
    fig.text(0.012, 0.012, wrapped, ha="left", va="bottom", fontsize=7.4, color=MUTED)
    return 0.02 + 0.022 * lines


def _style(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRID, zorder=0)
    ax.set_axisbelow(True)


def _save(fig: plt.Figure, path, bottom: float) -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=(0, bottom, 1, 1))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _finish(fig: plt.Figure, ax, source: str, path) -> None:
    _style(ax)
    bottom = _footnote(fig, source)
    _save(fig, path, bottom)


def chart_generation(annual: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10.2, 5.6))
    ax.plot(annual["year"], annual["ember_generation_twh"], color=EMBER, lw=2.2, label="Ember yearly")
    ax.plot(annual["year"], annual["eia_generation_twh"], color=EIA, lw=2.2, label="EIA")
    ax.plot(
        annual["year"],
        annual["owid_generation_twh"],
        color=OWID,
        lw=1.6,
        ls="--",
        label="Our World in Data (10 Sep 2026 release)",
    )
    nerc = annual[annual["nerc_generation_twh"].notna()]
    ax.scatter(
        nerc["year"],
        nerc["nerc_generation_twh"],
        color=NERC,
        s=46,
        zorder=4,
        label="NERC grid total",
    )
    for _, row in nerc.iterrows():
        ax.annotate(
            f"{row['nerc_generation_twh']:.1f}",
            (row["year"], row["nerc_generation_twh"]),
            textcoords="offset points",
            xytext=(6, 6),
            fontsize=8,
            color=NERC,
        )
    ax.set_title("Nigeria: the series agree for years, then they don't")
    ax.set_ylabel("Electricity generation (TWh)")
    ax.set_xlabel("Year")
    ax.set_xlim(1999.5, 2025.6)
    ax.legend(frameon=False, loc="upper left")
    _finish(
        fig,
        ax,
        "Ember yearly file and EIA international electricity CSV, downloaded 25 November 2026. "
        "OWID energy dataset, version 2026-09-10. NERC 2023 is the sum of four quarterly reports; "
        "2024 and 2025 are NERC annual reports. NERC is grid-connected generation only.",
        FIGURES / "01_nigeria_generation_by_source.png",
    )


def chart_fuels(fuels: pd.DataFrame) -> None:
    years = [2023, 2024, 2025]
    names = ["Gas", "Hydro", "Solar"]
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 4.8), sharey=False)
    for ax, fuel in zip(axes, names):
        part = fuels[(fuels["fuel"] == fuel) & (fuels["year"].isin(years))]
        x = np.arange(len(years))
        width = 0.36
        ember_vals = [float(part.loc[part["year"] == y, "ember_twh"].iloc[0]) for y in years]
        eia_vals = [float(part.loc[part["year"] == y, "eia_twh"].iloc[0]) for y in years]
        ax.bar(x - width / 2, ember_vals, width, color=EMBER, label="Ember", zorder=2)
        ax.bar(x + width / 2, eia_vals, width, color=EIA, label="EIA", zorder=2)
        ax.set_xticks(x, [str(y) for y in years])
        ax.set_title(fuel)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", color=GRID)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Generation (TWh)")
    axes[2].legend(frameon=False, loc="upper left")
    fig.suptitle("Where Ember and the EIA now disagree, by fuel", fontsize=13, y=1.02)
    bottom = _footnote(
        fig,
        "Same download as Figure 1. Solar is the series that breaks the physical check in Figure 3. "
        "Gas and hydro also differ, so the gap is not solar alone.",
    )
    _save(fig, FIGURES / "02_fuel_gap_ember_vs_eia.png", bottom)


def chart_solar_cf(fuels: pd.DataFrame, west: pd.DataFrame) -> None:
    solar = fuels[(fuels["fuel"] == "Solar") & (fuels["ember_capacity_gw"] > 0)].copy()
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 5.2), gridspec_kw={"width_ratios": [1.15, 1]})
    ax = axes[0]
    ax.plot(solar["year"], solar["ember_capacity_factor"] * 100, color=EMBER, lw=2.2, marker="o")
    ax.axhline(100, color="#B91C1C", lw=1, ls="--", label="100%: impossible if capacity is right")
    ax.axhline(50, color=MUTED, lw=1, ls=":", label="50%: more energy than all the daylight hours")
    ax.set_title("Nigeria solar, implied capacity factor")
    ax.set_ylabel("Capacity factor (%)")
    ax.set_xlabel("Year")
    ax.set_ylim(0, 150)
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRID)
    ax.set_axisbelow(True)

    ax2 = axes[1]
    peer = west[(west["year"] == 2024) & west["solar_capacity_factor"].notna()].sort_values(
        "solar_capacity_factor"
    )
    colours = [EMBER if c == "Nigeria" else "#9AA5B1" for c in peer["country"]]
    ax2.barh(peer["country"], peer["solar_capacity_factor"] * 100, color=colours, zorder=2)
    ax2.axvline(50, color=MUTED, lw=1, ls=":")
    ax2.axvline(100, color="#B91C1C", lw=1, ls="--")
    ax2.set_xlim(0, 150)
    ax2.set_title("ECOWAS, 2024")
    ax2.set_xlabel("Implied solar capacity factor (%)")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(axis="x", color=GRID)
    ax2.set_axisbelow(True)
    fig.suptitle(
        "Ember's solar generation and Ember's solar capacity cannot both be right",
        fontsize=13,
        y=1.02,
    )
    bottom = _footnote(
        fig,
        "Capacity factor = generation (TWh) / (capacity (GW) × hours in the year / 1,000). "
        "Hours are 8,784 in leap years. A solar fleet is idle at night, so a factor above 50% "
        "already means the generation and the capacity are not a consistent pair. Nigeria in 2025 is above 100%.",
    )
    _save(fig, FIGURES / "03_solar_capacity_factor.png", bottom)


def chart_monthly(monthly: pd.DataFrame) -> None:
    full = monthly[monthly["complete_year"]].copy()
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 5.0))
    for ax, source, title in (
        (axes[0], "Total generation", "Total generation"),
        (axes[1], "Solar", "Solar only"),
    ):
        part = full[full["source"] == source]
        ax.plot(part["year"], part["annual_twh"], color=EMBER, lw=2.2, marker="o", label="Ember annual")
        ax.plot(
            part["year"],
            part["monthly_sum_twh"],
            color="#0E7490",
            lw=2.2,
            marker="o",
            label="Sum of Ember monthly",
        )
        ax.set_title(title)
        ax.set_ylabel("TWh")
        ax.set_xlabel("Year")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", color=GRID)
        ax.set_axisbelow(True)
        ax.legend(frameon=False, fontsize=8)
    fig.suptitle("Adding up the monthly file does not recover the annual total", fontsize=13, y=1.02)
    bottom = _footnote(
        fig,
        "Ember methodology: monthly Nigeria generation is taken from TCN, and summing the months "
        "will not equal the annual values. Solar is the exception in this file: the monthly sum "
        "and the annual figure are almost the same, so the implausible solar number is in both. "
        "2026 is omitted because only eight months are in the file.",
    )
    _save(fig, FIGURES / "04_monthly_versus_annual.png", bottom)


def _band(frame: pd.DataFrame, metric: str) -> tuple[float, float]:
    row = frame.loc[frame["metric"] == metric].iloc[0]
    low = float(row["low"])
    high = float(row["high"])
    return low, high


def chart_offgrid(annual: pd.DataFrame, offgrid: pd.DataFrame) -> None:
    """Scale comparison. Captive studies are not spliced onto the grid series."""
    y2024 = annual.loc[annual["year"] == 2024].iloc[0]
    iea_low, iea_high = _band(offgrid, "backup_generation_twh")
    lowcarbon = offgrid.loc[offgrid["year_described"].astype(str) == "2009"].iloc[0]
    wide = offgrid.loc[offgrid["metric"] == "self_generation_twh"]
    wide = wide.loc[wide["central"].isna()].iloc[0]
    diesel_low, diesel_high = _band(offgrid, "diesel_genset_generation_twh")
    labels = [
        "NERC grid, 2024",
        "Ember, 2024",
        "EIA, 2024",
        "IEA back-up model, 2018",
        "World Bank low-carbon\nstudy, 2009",
        "World Bank range,\nmixed years ~2007–12",
        "World Bank diesel\ngensets only",
    ]
    centres = [
        float(y2024["nerc_generation_twh"]),
        float(y2024["ember_generation_twh"]),
        float(y2024["eia_generation_twh"]),
        iea_low,
        float(lowcarbon["central"]),
        (float(wide["low"]) + float(wide["high"])) / 2,
        (diesel_low + diesel_high) / 2,
    ]
    lows = [np.nan, np.nan, np.nan, np.nan, np.nan, float(wide["low"]), diesel_low]
    highs = [np.nan, np.nan, np.nan, np.nan, np.nan, float(wide["high"]), diesel_high]
    colours = [NERC, EMBER, EIA, "#92400E", "#92400E", "#92400E", "#92400E"]
    if iea_low != iea_high:
        raise RuntimeError("Expected the IEA Nigeria figure to be a point estimate.")
    fig, ax = plt.subplots(figsize=(10.2, 5.8))
    y = np.arange(len(labels))[::-1]
    for i, (centre, low, high, colour) in enumerate(zip(centres, lows, highs, colours)):
        yy = y[i]
        if np.isnan(low):
            ax.plot(centre, yy, "o", color=colour, ms=8, zorder=3)
        else:
            ax.plot([low, high], [yy, yy], color=colour, lw=2, zorder=2)
            ax.plot([low, high], [yy, yy], "|", color=colour, ms=10, zorder=3)
    ax.set_yticks(y, labels)
    ax.set_xlabel("Terawatt-hours")
    ax.set_title("Grid statistics and captive generation are different objects")
    ax.set_xlim(0, 48)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color=GRID)
    ax.set_axisbelow(True)
    bottom = _footnote(
        fig,
        "Brown marks are published estimates of fossil self-generation, each with its own year and method. "
        "They are drawn on the same axis so the scale is visible. They are not added to the 2024 grid totals. "
        "IEA Africa Energy Outlook 2019; World Bank diesel-genset study, 2014. "
        "IFC capacity figures (GW) are left off this energy chart.",
    )
    _save(fig, FIGURES / "05_grid_and_captive_generation.png", bottom)
    # offgrid argument keeps the linter honest: the table is the source of the plotted studies
    assert {"backup_generation_twh", "self_generation_twh"} <= set(offgrid["metric"])


def chart_west_africa(west: pd.DataFrame) -> None:
    part = (
        west[west["year"] == 2024]
        .dropna(subset=["ember_kwh_per_person"])
        .sort_values("ember_kwh_per_person")
    )
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 5.4))
    colours = [EMBER if c == "Nigeria" else "#9AA5B1" for c in part["country"]]
    axes[0].barh(part["country"], part["ember_kwh_per_person"], color=colours, zorder=2)
    axes[0].set_xlabel("Ember generation per person (kWh)")
    axes[0].set_title("Generation per person")
    gap = west[west["year"] == 2024].sort_values("ember_minus_eia_pct")
    colours = [EMBER if c == "Nigeria" else "#9AA5B1" for c in gap["country"]]
    axes[1].barh(gap["country"], gap["ember_minus_eia_pct"], color=colours, zorder=2)
    axes[1].axvline(0, color=INK, lw=0.8)
    axes[1].set_xlabel("Ember minus EIA, per cent of EIA")
    axes[1].set_title("The same vintage gap, across ECOWAS")
    for ax in axes:
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="x", color=GRID)
        ax.set_axisbelow(True)
    fig.suptitle(
        "West Africa, 2024: generation per person, and the Ember–EIA gap",
        fontsize=13,
        y=1.02,
    )
    bottom = _footnote(
        fig,
        "Per person uses Ember generation and Our World in Data's population series. "
        "It is statistical generation, not electricity used, and it excludes captive generators. "
        "A negative bar means Ember's total is below the EIA file downloaded the same day. "
        "Nigeria's percentage gap is smaller than several neighbours; the solar problem in Figure 3 is not.",
    )
    _save(fig, FIGURES / "06_west_africa_context.png", bottom)


def make_charts(annual, fuels, monthly, west, offgrid) -> None:
    chart_generation(annual)
    chart_fuels(fuels)
    chart_solar_cf(fuels, west)
    chart_monthly(monthly)
    chart_offgrid(annual, offgrid)
    chart_west_africa(west)
