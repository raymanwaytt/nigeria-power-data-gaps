"""Compare Ember, EIA, Our World in Data and NERC on one definition of a year."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from nigeria_power.config import (
    ECOWAS,
    EIA_FUEL,
    FUELS,
    OWID_PAGE,
    OWID_VERSION,
    PROCESSED,
    SLICES,
    WB_DIR,
)


def hours_in_year(year: int) -> int:
    leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    return 8784 if leap else 8760


def load_frames() -> dict[str, pd.DataFrame]:
    ember = pd.read_csv(SLICES / "ember_yearly_ecowas.csv")
    ember["Year"] = ember["Year"].astype(int)
    monthly = pd.read_csv(SLICES / "ember_monthly_nigeria.csv")
    monthly["year"] = pd.to_datetime(monthly["Date"]).dt.year
    owid = pd.read_csv(SLICES / "owid_energy_ecowas.csv")
    eia = pd.read_csv(SLICES / "eia_electricity_ecowas.csv")
    eia["year"] = pd.to_datetime(eia["DATE"], format="%d-%b-%Y").dt.year
    eia["value"] = pd.to_numeric(eia["DATAVALUE_UNROUNDED"], errors="coerce")
    return {"ember": ember, "monthly": monthly, "owid": owid, "eia": eia}


def _ember_series(ember: pd.DataFrame, iso: str, source: str, column: str) -> pd.Series:
    part = ember[(ember["ISO 3 code"] == iso) & (ember["Electricity source"] == source)]
    return part.set_index("Year")[column].astype(float)


def nigeria_annual(frames: dict[str, pd.DataFrame], nerc: pd.DataFrame) -> pd.DataFrame:
    ember = frames["ember"]
    eia = frames["eia"]
    owid = frames["owid"]
    total = _ember_series(ember, "NGA", "Total generation", "Generation (TWh)")
    demand = _ember_series(ember, "NGA", "Demand", "Generation (TWh)")
    imports = _ember_series(ember, "NGA", "Net imports", "Generation (TWh)")
    eia_gen = _eia_nigeria(eia, "generation", "electricity")
    eia_cons = _eia_nigeria(eia, "consumption", "electricity")
    eia_loss = _eia_nigeria(eia, "distribution losses", "electricity")
    eia_exp = _eia_nigeria(eia, "exports", "electricity")
    eia_imp = _eia_nigeria(eia, "imports", "electricity")
    owid_n = owid[owid["iso_code"] == "NGA"].set_index("year")

    nerc_annual = nerc[(nerc["metric"] == "grid_generation_gwh") & nerc["quarter"].isna()]
    nerc_map = nerc_annual.set_index("year")["value_twh"]
    q = nerc[(nerc["metric"] == "grid_generation_gwh") & nerc["quarter"].notna()]
    q2023 = q[q["year"] == 2023]["value_twh"].sum()

    rows = []
    for year in sorted(total.index):
        eia_value = eia_gen.get(year, np.nan)
        owid_value = (
            float(owid_n.loc[year, "electricity_generation_twh"])
            if year in owid_n.index
            else np.nan
        )
        balance = np.nan
        if year in eia_cons.index:
            balance = (
                eia_cons.get(year, 0)
                + eia_loss.get(year, 0)
                + eia_exp.get(year, 0)
                - eia_imp.get(year, 0)
            )
        nerc_value = np.nan
        nerc_note = ""
        if year in nerc_map.index:
            nerc_value = float(nerc_map.loc[year])
            nerc_note = "NERC annual report"
        elif year == 2023:
            nerc_value = float(q2023)
            nerc_note = "Sum of four NERC quarterly totals"
        gap = float(total.loc[year]) - float(eia_value) if pd.notna(eia_value) else np.nan
        rows.append(
            {
                "year": int(year),
                "ember_generation_twh": float(total.loc[year]),
                "ember_demand_twh": float(demand.loc[year]) if year in demand.index else np.nan,
                "ember_net_imports_twh": float(imports.loc[year]) if year in imports.index else np.nan,
                "eia_generation_twh": float(eia_value) if pd.notna(eia_value) else np.nan,
                "eia_balance_twh": float(balance) if pd.notna(balance) else np.nan,
                "owid_generation_twh": owid_value,
                "nerc_generation_twh": nerc_value,
                "nerc_note": nerc_note,
                "ember_minus_eia_twh": gap,
                "ember_minus_eia_pct": (gap / float(eia_value) * 100) if pd.notna(eia_value) and eia_value else np.nan,
                "population": (
                    float(owid_n.loc[year, "population"]) if year in owid_n.index else np.nan
                ),
            }
        )
    frame = pd.DataFrame(rows)
    # Accounting identity inside Ember: demand should equal generation + net imports.
    frame["ember_identity_gap_twh"] = (
        frame["ember_generation_twh"] + frame["ember_net_imports_twh"] - frame["ember_demand_twh"]
    )
    frame["eia_identity_gap_twh"] = frame["eia_generation_twh"] - frame["eia_balance_twh"]
    frame.to_csv(PROCESSED / "nigeria_annual_comparison.csv", index=False)
    return frame


def _eia_nigeria(eia: pd.DataFrame, activity: str, product: str) -> pd.Series:
    part = eia[
        (eia["GEOGRAPHY"] == "Nigeria")
        & (eia["ACTIVITY"] == activity)
        & (eia["PRODUCT"] == product)
        & (eia["UNIT"] == "BKWH")
    ]
    return part.groupby("year")["value"].first()


def fuel_comparison(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    ember = frames["ember"]
    eia = frames["eia"]
    owid = frames["owid"]
    owid_n = owid[owid["iso_code"] == "NGA"].set_index("year")
    owid_col = {
        "Gas": "gas_electricity_twh",
        "Hydro": "hydro_electricity_twh",
        "Solar": "solar_electricity_twh",
        "Bioenergy": "bioenergy_electricity_twh",
        "Coal": "coal_electricity_twh",
        "Wind": "wind_electricity_twh",
    }
    rows = []
    for year in range(2000, 2026):
        for fuel in FUELS:
            emb = ember[
                (ember["ISO 3 code"] == "NGA")
                & (ember["Year"] == year)
                & (ember["Electricity source"] == fuel)
            ]
            if emb.empty:
                continue
            gen = float(emb["Generation (TWh)"].iloc[0])
            cap = emb["Capacity (GW)"].iloc[0]
            cap = float(cap) if pd.notna(cap) and str(cap) != "" else np.nan
            eia_product = EIA_FUEL.get(fuel)
            eia_value = np.nan
            if eia_product:
                hit = eia[
                    (eia["GEOGRAPHY"] == "Nigeria")
                    & (eia["year"] == year)
                    & (eia["ACTIVITY"] == "generation")
                    & (eia["PRODUCT"] == eia_product)
                    & (eia["UNIT"] == "BKWH")
                ]
                if not hit.empty:
                    eia_value = float(hit["value"].iloc[0])
            owid_value = np.nan
            if fuel in owid_col and year in owid_n.index:
                owid_value = float(owid_n.loc[year, owid_col[fuel]])
            hours = hours_in_year(year)
            cf = gen / (cap * hours / 1000) if pd.notna(cap) and cap > 0 else np.nan
            rows.append(
                {
                    "year": year,
                    "fuel": fuel,
                    "ember_twh": gen,
                    "ember_capacity_gw": cap,
                    "ember_capacity_factor": cf,
                    "hours_in_year": hours,
                    "eia_twh": eia_value,
                    "owid_twh": owid_value,
                    "ember_minus_eia_twh": gen - eia_value if pd.notna(eia_value) else np.nan,
                }
            )
    frame = pd.DataFrame(rows)
    frame.to_csv(PROCESSED / "nigeria_fuel_comparison.csv", index=False)
    return frame


def monthly_vs_annual(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    monthly = frames["monthly"]
    ember = frames["ember"]
    sources = ["Total generation", "Gas", "Hydro", "Solar"]
    rows = []
    for year, part in monthly.groupby("year"):
        counts = part[part["Electricity source"] == "Total generation"].shape[0]
        for source in sources:
            sub = part[part["Electricity source"] == source]
            monthly_sum = float(sub["Generation (TWh)"].sum()) if not sub.empty else np.nan
            annual = ember[
                (ember["ISO 3 code"] == "NGA")
                & (ember["Year"] == int(year))
                & (ember["Electricity source"] == source)
            ]
            annual_value = float(annual["Generation (TWh)"].iloc[0]) if not annual.empty else np.nan
            rows.append(
                {
                    "year": int(year),
                    "source": source,
                    "months_reported": int(counts),
                    "complete_year": counts == 12,
                    "monthly_sum_twh": monthly_sum,
                    "annual_twh": annual_value,
                    "annual_minus_monthly_twh": (
                        annual_value - monthly_sum
                        if pd.notna(annual_value) and pd.notna(monthly_sum)
                        else np.nan
                    ),
                }
            )
    frame = pd.DataFrame(rows)
    frame.to_csv(PROCESSED / "nigeria_monthly_vs_annual.csv", index=False)
    return frame


def west_africa(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    ember = frames["ember"]
    eia = frames["eia"]
    owid = frames["owid"]
    rows = []
    for country in ECOWAS:
        for year in (2023, 2024, 2025):
            emb = ember[
                (ember["ISO 3 code"] == country["iso3"])
                & (ember["Year"] == year)
                & (ember["Electricity source"] == "Total generation")
            ]
            if emb.empty:
                continue
            gen = float(emb["Generation (TWh)"].iloc[0])
            hit = eia[
                (eia["GEOGRAPHY"] == country["eia"])
                & (eia["year"] == year)
                & (eia["ACTIVITY"] == "generation")
                & (eia["PRODUCT"] == "electricity")
                & (eia["UNIT"] == "BKWH")
            ]
            eia_value = float(hit["value"].iloc[0]) if not hit.empty else np.nan
            pop_row = owid[(owid["country"] == country["owid"]) & (owid["year"] == year)]
            population = float(pop_row["population"].iloc[0]) if not pop_row.empty else np.nan
            solar = ember[
                (ember["ISO 3 code"] == country["iso3"])
                & (ember["Year"] == year)
                & (ember["Electricity source"] == "Solar")
            ]
            solar_gen = float(solar["Generation (TWh)"].iloc[0]) if not solar.empty else np.nan
            solar_cap = (
                float(solar["Capacity (GW)"].iloc[0])
                if not solar.empty and pd.notna(solar["Capacity (GW)"].iloc[0])
                else np.nan
            )
            cf = (
                solar_gen / (solar_cap * hours_in_year(year) / 1000)
                if pd.notna(solar_cap) and solar_cap > 0 and pd.notna(solar_gen)
                else np.nan
            )
            gap = gen - eia_value if pd.notna(eia_value) else np.nan
            rows.append(
                {
                    "country": country["area"],
                    "iso3": country["iso3"],
                    "year": year,
                    "ember_twh": gen,
                    "eia_twh": eia_value,
                    "ember_minus_eia_twh": gap,
                    "ember_minus_eia_pct": (gap / eia_value * 100) if pd.notna(eia_value) and eia_value else np.nan,
                    "population": population,
                    "ember_kwh_per_person": (
                        gen * 1e9 / population if pd.notna(population) and population else np.nan
                    ),
                    "solar_twh": solar_gen,
                    "solar_capacity_gw": solar_cap,
                    "solar_capacity_factor": cf,
                }
            )
    frame = pd.DataFrame(rows)
    frame.to_csv(PROCESSED / "west_africa_comparison.csv", index=False)
    return frame


def world_bank_access() -> dict:
    payload = json.loads((WB_DIR / "EG.ELC.ACCS.ZS.json").read_text())
    records = [row for row in payload[1] if row and row.get("value") is not None]
    latest = max(records, key=lambda row: int(row["date"]))
    return {
        "indicator": latest["indicator"]["id"],
        "name": latest["indicator"]["value"],
        "year": int(latest["date"]),
        "value_percent": float(latest["value"]),
        "lastupdated": payload[0].get("lastupdated"),
        "url": "https://api.worldbank.org/v2/country/NGA/indicator/EG.ELC.ACCS.ZS?format=json",
    }


def build_findings(
    annual: pd.DataFrame,
    fuels: pd.DataFrame,
    monthly: pd.DataFrame,
    west: pd.DataFrame,
    nerc: pd.DataFrame,
    access: dict,
) -> dict:
    def row_year(year: int) -> pd.Series:
        return annual.loc[annual["year"] == year].iloc[0]

    y2024 = row_year(2024)
    y2025 = row_year(2025)
    y2015 = row_year(2015)
    solar = fuels[(fuels["fuel"] == "Solar")].set_index("year")
    # First year the Ember–EIA gap is larger than half a tenth of a TWh.
    diverged = annual[annual["ember_minus_eia_twh"].abs() > 0.05]
    first_gap_year = int(diverged["year"].min()) if not diverged.empty else None

    q2025 = nerc[
        (nerc["year"] == 2025)
        & (nerc["metric"] == "grid_generation_gwh")
        & nerc["quarter"].notna()
    ]
    quarterly_sum_2025 = float(q2025["value_gwh"].sum())
    annual_2025_gwh = float(
        nerc[
            (nerc["year"] == 2025)
            & (nerc["metric"] == "grid_generation_gwh")
            & nerc["quarter"].isna()
        ]["value_gwh"].iloc[0]
    )

    wa_2024 = west[west["year"] == 2024].sort_values("ember_minus_eia_pct")
    high_cf = west[(west["year"] == 2024) & (west["solar_capacity_factor"] > 0.5)]

    findings = {
        "question": (
            "Can Ember's published electricity generation series for Nigeria be used "
            "as a measure of electricity output, once it is checked against the EIA "
            "series Ember says it comes from, against Ember's own capacity figures, "
            "against NERC's grid statistics, and against the captive generation those "
            "grid statistics leave out?"
        ),
        "owid_version": OWID_VERSION,
        "owid_page": OWID_PAGE,
        "first_year_ember_eia_gap_above_0_05_twh": first_gap_year,
        "year_2015_ember_twh": round(float(y2015["ember_generation_twh"]), 3),
        "year_2015_eia_twh": round(float(y2015["eia_generation_twh"]), 3),
        "year_2024": {
            "ember_twh": round(float(y2024["ember_generation_twh"]), 3),
            "eia_twh": round(float(y2024["eia_generation_twh"]), 3),
            "owid_twh": round(float(y2024["owid_generation_twh"]), 3),
            "nerc_twh": round(float(y2024["nerc_generation_twh"]), 3),
            "ember_minus_eia_twh": round(float(y2024["ember_minus_eia_twh"]), 3),
            "ember_minus_eia_pct": round(float(y2024["ember_minus_eia_pct"]), 2),
            "kwh_per_person_ember": round(
                float(y2024["ember_generation_twh"]) * 1e9 / float(y2024["population"]), 1
            ),
            "kwh_per_person_nerc": round(
                float(y2024["nerc_generation_twh"]) * 1e9 / float(y2024["population"]), 1
            ),
            "population": float(y2024["population"]),
        },
        "year_2025": {
            "ember_twh": round(float(y2025["ember_generation_twh"]), 3),
            "eia_twh": round(float(y2025["eia_generation_twh"]), 3),
            "owid_twh": round(float(y2025["owid_generation_twh"]), 3),
            "nerc_twh": round(float(y2025["nerc_generation_twh"]), 3),
            "ember_minus_eia_twh": round(float(y2025["ember_minus_eia_twh"]), 3),
            "ember_minus_nerc_twh": round(
                float(y2025["ember_generation_twh"] - y2025["nerc_generation_twh"]), 3
            ),
        },
        "solar": {
            str(year): {
                "ember_twh": round(float(solar.loc[year, "ember_twh"]), 3),
                "capacity_gw": round(float(solar.loc[year, "ember_capacity_gw"]), 2),
                "capacity_factor": round(float(solar.loc[year, "ember_capacity_factor"]), 3),
                "eia_twh": round(float(solar.loc[year, "eia_twh"]), 3),
                "owid_twh": None
                if pd.isna(solar.loc[year, "owid_twh"])
                else round(float(solar.loc[year, "owid_twh"]), 3),
            }
            for year in (2019, 2021, 2023, 2024, 2025)
        },
        "nerc_2025_quarterly_sum_gwh": round(quarterly_sum_2025, 2),
        "nerc_2025_annual_gwh": annual_2025_gwh,
        "nerc_2025_annual_minus_quarters_gwh": round(annual_2025_gwh - quarterly_sum_2025, 2),
        "max_abs_ember_identity_gap_twh": round(float(annual["ember_identity_gap_twh"].abs().max()), 4),
        "max_abs_eia_identity_gap_twh": round(float(annual["eia_identity_gap_twh"].abs().max()), 4),
        "monthly_2024_total_twh": round(
            float(
                monthly[
                    (monthly["year"] == 2024) & (monthly["source"] == "Total generation")
                ]["monthly_sum_twh"].iloc[0]
            ),
            3,
        ),
        "west_africa_2024_largest_shortfall": wa_2024.nsmallest(3, "ember_minus_eia_pct")[
            ["country", "ember_minus_eia_pct", "ember_twh", "eia_twh"]
        ].to_dict(orient="records"),
        "west_africa_2024_solar_cf_above_50pct": high_cf[
            ["country", "solar_capacity_factor", "solar_twh", "solar_capacity_gw"]
        ].to_dict(orient="records"),
        "access_to_electricity": access,
        "hydro_2024": {
            "nerc_twh": round(
                float(
                    nerc[
                        (nerc["year"] == 2024) & (nerc["metric"] == "hydro_generation_gwh")
                    ]["value_twh"].iloc[0]
                ),
                3,
            ),
            "ember_twh": round(float(fuels[(fuels.year == 2024) & (fuels.fuel == "Hydro")]["ember_twh"].iloc[0]), 3),
            "eia_twh": round(float(fuels[(fuels.year == 2024) & (fuels.fuel == "Hydro")]["eia_twh"].iloc[0]), 3),
        },
    }
    (PROCESSED / "findings.json").write_text(json.dumps(findings, indent=2))
    return findings
