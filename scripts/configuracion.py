"""Configuracion compartida del pipeline de datos."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW = DATA_DIR / "raw"
DATA_PROCESSED = DATA_DIR / "processed"
OUTPUT_CLEAN = PROJECT_ROOT / "homicidios_clean.csv"
OUTPUT_CONSOLIDATED = DATA_PROCESSED / "homicidios_consolidado.csv"
SOURCE_MANIFEST = DATA_DIR / "source_manifest.json"

CKAN_DATASET_API = (
    "https://www.datosabiertos.gob.ec/api/3/action/"
    "package_show?id=homicidios-intencionales"
)

# Estos nombres no cambian cada mes. El contenido se reemplaza de forma
# atomica cuando el Ministerio publica una revision.
CANONICAL_SOURCES = {
    "historico": DATA_RAW / "mdi_homicidios_intencionales_pm_historico.xlsx",
    "actual": DATA_RAW / "mdi_homicidios_intencionales_pm_actual.xlsx",
}
