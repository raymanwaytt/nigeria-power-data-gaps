"""Paths, country lists and publisher URLs.

Figures are not stored here. This module only names files and where they came from.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
CACHE = RAW / "cache"
SLICES = RAW / "slices"
NERC_DIR = RAW / "nerc"
LIT_DIR = RAW / "literature"
EMBER_DIR = RAW / "ember"
WB_DIR = RAW / "worldbank"
EIA_META = RAW / "eia" / "metadata.json"
PROCESSED = DATA / "processed"
FIGURES = ROOT / "outputs" / "figures"
OUTPUTS = ROOT / "outputs"

# ECOWAS members. Cabo Verde is included; Mauritania is not a member.
ECOWAS = [
    {"area": "Benin", "iso3": "BEN", "eia": "Benin", "owid": "Benin"},
    {"area": "Burkina Faso", "iso3": "BFA", "eia": "Burkina Faso", "owid": "Burkina Faso"},
    {"area": "Cabo Verde", "iso3": "CPV", "eia": "Cabo Verde", "owid": "Cape Verde"},
    {"area": "Cote d'Ivoire", "iso3": "CIV", "eia": "Cote d'Ivoire", "owid": "Cote d'Ivoire"},
    {"area": "Gambia", "iso3": "GMB", "eia": "Gambia, The", "owid": "Gambia"},
    {"area": "Ghana", "iso3": "GHA", "eia": "Ghana", "owid": "Ghana"},
    {"area": "Guinea", "iso3": "GIN", "eia": "Guinea", "owid": "Guinea"},
    {"area": "Guinea-Bissau", "iso3": "GNB", "eia": "Guinea-Bissau", "owid": "Guinea-Bissau"},
    {"area": "Liberia", "iso3": "LBR", "eia": "Liberia", "owid": "Liberia"},
    {"area": "Mali", "iso3": "MLI", "eia": "Mali", "owid": "Mali"},
    {"area": "Niger", "iso3": "NER", "eia": "Niger", "owid": "Niger"},
    {"area": "Nigeria", "iso3": "NGA", "eia": "Nigeria", "owid": "Nigeria"},
    {"area": "Senegal", "iso3": "SEN", "eia": "Senegal", "owid": "Senegal"},
    {"area": "Sierra Leone", "iso3": "SLE", "eia": "Sierra Leone", "owid": "Sierra Leone"},
    {"area": "Togo", "iso3": "TGO", "eia": "Togo", "owid": "Togo"},
]

EMBER_YEARLY_URL = (
    "https://files.ember-energy.org/public-downloads/generation/outputs/"
    "release_generation_yearly_global.csv"
)
EMBER_MONTHLY_URL = (
    "https://files.ember-energy.org/public-downloads/generation/outputs/"
    "release_generation_monthly_global.csv"
)
EMBER_METHOD_URL = (
    "https://files.ember-energy.org/public-downloads/ember_electricity_data_methodology.pdf"
)
EMBER_PAGE = "https://ember-energy.org/data/yearly-electricity-data/"

EIA_ELECTRICITY_URL = "https://www.eia.gov/international/data/csv/electricity_annual.csv"
EIA_METADATA_URL = "https://www.eia.gov/international/data/csv/metadata.json"
EIA_PAGE = "https://www.eia.gov/international/data/"

OWID_URL = "https://catalog.ourworldindata.org/garden/energy/2026-09-10/owid_energy/owid_energy.csv"
OWID_PAGE = "https://catalog.ourworldindata.org/energy/owid_energy/"
OWID_VERSION = "2026-09-10"
OWID_CODEBOOK_URL = "https://catalog.ourworldindata.org/energy/owid_energy/owid_energy.codebook.csv"
OWID_SOURCES_URL = "https://catalog.ourworldindata.org/energy/owid_energy/owid_energy.sources.csv"

WB_ACCESS_URL = (
    "https://api.worldbank.org/v2/country/NGA/indicator/EG.ELC.ACCS.ZS?format=json&per_page=200"
)
WB_PROD_URL = (
    "https://api.worldbank.org/v2/country/NGA/indicator/EG.ELC.PROD.KH?format=json&per_page=200"
)

IEA_AEO_URL = (
    "https://iea.blob.core.windows.net/assets/2f7b6170-d616-4dd7-a7ca-a65a3a332fc1/"
    "Africa_Energy_Outlook_2019.pdf"
)
IEA_AEO_PAGE = "https://www.iea.org/reports/africa-energy-outlook-2019"
IEA_BROWSER = "https://www.iea.org/data-and-statistics/data-tools/energy-statistics-data-browser"

# Published SHA-256 of electricity_annual.csv in EIA metadata dated 2026-11-19.
# The download step checks the file against the checksum inside the metadata
# actually downloaded, and this constant is only a record of the value seen
# on 25 November 2026.
EIA_SHA256_SEEN = "d1830e20b062c8d67dc50c62117c5dc0fc73579ce57593c6bba77829a0b93b26"
EIA_BYTES_SEEN = 108255548

FUELS = ["Gas", "Hydro", "Solar", "Bioenergy", "Coal", "Wind", "Other fossil", "Nuclear"]
EIA_FUEL = {
    "Gas": "natural gas",
    "Hydro": "hydroelectricity",
    "Solar": "solar",
    "Bioenergy": "biomass and waste",
    "Coal": "coal",
    "Wind": "wind",
    "Nuclear": "nuclear",
    "Oil": "oil",
}
