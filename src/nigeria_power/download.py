"""Download publisher files and write the small slices the analysis reads.

Full international CSVs are kept in data/raw/cache, which is gitignored.
The EIA electricity file is about 108 MB and is accepted only when its
SHA-256 matches the checksum EIA publishes in metadata.json.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

from nigeria_power.config import (
    CACHE,
    EIA_ELECTRICITY_URL,
    EIA_META,
    EIA_METADATA_URL,
    EMBER_DIR,
    EMBER_METHOD_URL,
    EMBER_MONTHLY_URL,
    EMBER_YEARLY_URL,
    LIT_DIR,
    OWID_CODEBOOK_URL,
    OWID_SOURCES_URL,
    OWID_URL,
    SLICES,
    WB_ACCESS_URL,
    WB_DIR,
    WB_PROD_URL,
    ECOWAS,
    IEA_AEO_URL,
)

csv.field_size_limit(sys.maxsize)

USER_AGENT = "nigeria-power-data-reconciliation/1.0 (public-data; research)"
DOWNLOAD_DATE = date.today().isoformat()


def _fetch(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(request, timeout=180) as response, tmp.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            handle.write(chunk)
    tmp.replace(dest)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_sources() -> None:
    """Refresh publisher files. Safe to re-run."""
    CACHE.mkdir(parents=True, exist_ok=True)
    jobs = [
        (EMBER_YEARLY_URL, CACHE / "ember_yearly_global.csv"),
        (EMBER_MONTHLY_URL, CACHE / "ember_monthly_global.csv"),
        (EMBER_METHOD_URL, EMBER_DIR / "ember_electricity_data_methodology.pdf"),
        (OWID_URL, CACHE / "owid_energy.csv"),
        (OWID_CODEBOOK_URL, CACHE / "owid_energy_codebook.csv"),
        (OWID_SOURCES_URL, CACHE / "owid_energy_sources.csv"),
        (EIA_METADATA_URL, EIA_META),
        (EIA_ELECTRICITY_URL, CACHE / "eia_electricity_annual.csv"),
        (WB_ACCESS_URL, WB_DIR / "EG.ELC.ACCS.ZS.json"),
        (IEA_AEO_URL, LIT_DIR / "iea_africa_energy_outlook_2019.pdf"),
    ]
    for url, dest in jobs:
        print(f"Downloading {url}")
        _fetch(url, dest)
    _check_eia_checksum(CACHE / "eia_electricity_annual.csv")
    _record_world_bank_production_attempt()


def _check_eia_checksum(path: Path) -> None:
    meta = json.loads(EIA_META.read_text())
    expected = None
    expected_size = None
    for dataset in meta.get("dataset", []):
        if dataset.get("identifier") != "electricity_annual":
            continue
        dist = dataset["distribution"][0]
        expected = dist["checksum"]["checksumValue"]
        expected_size = dist["byteSize"]
    if not expected:
        raise RuntimeError("EIA metadata did not contain an electricity_annual checksum.")
    actual = sha256(path)
    if actual != expected or path.stat().st_size != int(expected_size):
        raise RuntimeError(
            "EIA electricity CSV failed the publisher checksum. "
            f"size={path.stat().st_size} expected_size={expected_size} "
            f"sha256={actual} expected={expected}. "
            "A truncated download is not usable."
        )
    print(f"EIA checksum matches metadata ({expected[:12]}…).")


def _record_world_bank_production_attempt() -> None:
    """EG.ELC.PROD.KH (electricity production) has been withdrawn from the live API."""
    dest = WB_DIR / "EG.ELC.PROD.KH_response.json"
    try:
        _fetch(WB_PROD_URL, dest)
    except Exception as exc:  # noqa: BLE001 — record the failure, do not invent a series
        dest.write_text(json.dumps({"error": str(exc), "url": WB_PROD_URL}))
        return


def _eia_names() -> set[str]:
    return {row["eia"] for row in ECOWAS}


def _ember_iso() -> set[str]:
    return {row["iso3"] for row in ECOWAS}


def _owid_names() -> set[str]:
    return {row["owid"] for row in ECOWAS}


def write_slices() -> dict:
    """Cut West Africa out of the cached full files. Returns a manifest."""
    SLICES.mkdir(parents=True, exist_ok=True)
    yearly_cache = CACHE / "ember_yearly_global.csv"
    monthly_cache = CACHE / "ember_monthly_global.csv"
    owid_cache = _first_existing(
        [CACHE / "owid_energy.csv", CACHE / "owid_energy_2026-09-10.csv"]
    )
    eia_cache = CACHE / "eia_electricity_annual.csv"
    for path in (yearly_cache, monthly_cache, owid_cache, eia_cache):
        if not path.exists():
            raise FileNotFoundError(
                f"Missing {path}. Run with --download, or keep the cached publisher files."
            )

    iso = _ember_iso()
    yearly = pd.read_csv(yearly_cache)
    yearly = yearly[yearly["ISO 3 code"].isin(iso)]
    yearly_path = SLICES / "ember_yearly_ecowas.csv"
    yearly.to_csv(yearly_path, index=False)

    monthly = pd.read_csv(monthly_cache)
    monthly = monthly[monthly["ISO 3 code"] == "NGA"]
    monthly_path = SLICES / "ember_monthly_nigeria.csv"
    monthly.to_csv(monthly_path, index=False)

    owid_cols = [
        "country",
        "year",
        "iso_code",
        "population",
        "electricity_generation_twh",
        "electricity_demand_twh",
        "electricity_net_imports_twh",
        "gas_electricity_twh",
        "hydro_electricity_twh",
        "solar_electricity_twh",
        "oil_electricity_twh",
        "bioenergy_electricity_twh",
        "coal_electricity_twh",
        "wind_electricity_twh",
    ]
    owid = pd.read_csv(owid_cache, usecols=lambda c: c in set(owid_cols))
    owid = owid[owid["country"].isin(_owid_names())]
    owid_path = SLICES / "owid_energy_ecowas.csv"
    owid.to_csv(owid_path, index=False)

    eia_path = SLICES / "eia_electricity_ecowas.csv"
    _slice_eia(eia_cache, eia_path)

    manifest = {
        "download_date": DOWNLOAD_DATE,
        "note": (
            "Slices are rows for ECOWAS countries cut from the publisher files. "
            "Full CSVs are not committed because the EIA file is over 100 MB. "
            "Re-download with python run_analysis.py --download."
        ),
        "files": [
            _file_record(EMBER_YEARLY_URL, yearly_cache, yearly_path, len(yearly)),
            _file_record(EMBER_MONTHLY_URL, monthly_cache, monthly_path, len(monthly)),
            _file_record(OWID_URL, owid_cache, owid_path, len(owid)),
            _file_record(EIA_ELECTRICITY_URL, eia_cache, eia_path, _count_rows(eia_path)),
        ],
    }
    (SLICES / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"Wrote slices to {SLICES}")
    return manifest


def _first_existing(paths: list[Path]) -> Path:
    for path in paths:
        if path.exists():
            return path
    return paths[0]


def _count_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        return max(sum(1 for _ in handle) - 1, 0)


def _file_record(url: str, full: Path, slice_path: Path, slice_rows: int) -> dict:
    return {
        "url": url,
        "full_file": full.name,
        "full_bytes": full.stat().st_size,
        "full_sha256": sha256(full),
        "slice": str(slice_path.relative_to(slice_path.parents[2])),
        "slice_rows": slice_rows,
        "slice_sha256": sha256(slice_path),
    }


def _slice_eia(src: Path, dest: Path) -> None:
    wanted = _eia_names()
    with src.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        width = len(header)
        with dest.open("w", newline="", encoding="utf-8") as out:
            writer = csv.writer(out)
            writer.writerow(header)
            kept = 0
            skipped = 0
            for row in reader:
                if len(row) != width:
                    skipped += 1
                    continue
                if row[1] in wanted and row[4] in {"BKWH", "MMKW"}:
                    writer.writerow(row)
                    kept += 1
    if kept < 1000:
        raise RuntimeError(f"EIA slice looks empty ({kept} rows, {skipped} malformed).")
