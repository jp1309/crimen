"""Consolida las fuentes oficiales y genera el CSV de produccion.

La fuente del anio en curso es acumulativa: cuando cambia, se procesa completa
para incorporar tanto el mes nuevo como las revisiones de meses anteriores.

Uso:
    python -m scripts.consolidar_y_limpiar
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import pandas as pd

from scripts.configuracion import (
    CANONICAL_SOURCES,
    DATA_PROCESSED,
    DATA_RAW,
    OUTPUT_CLEAN,
    OUTPUT_CONSOLIDATED,
)


MESES = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}


def get_month_value(filename: str) -> int:
    """Obtiene el ultimo mes de cobertura indicado en un nombre legado."""

    parts = Path(filename).stem.lower().replace("_", " ").replace("-", " ").split()
    if "enero" in parts and "diciembre" in parts:
        return 13
    month = max((MESES.get(part, 0) for part in parts), default=0)
    if month:
        return month
    return max((int(part) for part in parts if part.isdigit() and 1 <= int(part) <= 12), default=0)


def smart_read_excel(path: str | Path, desc: str) -> pd.DataFrame:
    """Localiza automaticamente la hoja y la fila de encabezado oficiales."""

    path = Path(path)
    print(f"Leyendo {desc} ({path.name})...")
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    try:
        workbook = pd.ExcelFile(path)
    except Exception as exc:
        raise ValueError(f"No se pudo abrir {path.name}: {exc}") from exc

    for sheet in workbook.sheet_names:
        try:
            preview = pd.read_excel(workbook, sheet_name=sheet, header=None, nrows=50)
        except Exception:
            continue
        for row_number, row in preview.iterrows():
            row_text = " ".join(str(value).upper() for value in row.values if pd.notna(value))
            if "PROVINCIA" in row_text and any(
                token in row_text for token in ("FECHA", "ZONA", "CANTON")
            ):
                print(f"  -> Datos en hoja '{sheet}', encabezado fila {row_number + 1}")
                return pd.read_excel(workbook, sheet_name=sheet, header=row_number)

    raise ValueError(f"No se detecto una tabla de datos valida en {path.name}")


def _detectar_archivos_legados() -> tuple[Path | None, Path | None]:
    files = [
        path
        for path in DATA_RAW.glob("*.xlsx")
        if not path.name.startswith("~$") and path not in CANONICAL_SOURCES.values()
    ]
    historical: Path | None = None
    partials: list[Path] = []

    for path in files:
        years = re.findall(r"20\d{2}", path.name)
        if len(years) >= 2 and years[0] != years[-1]:
            if historical is None:
                historical = path
            else:
                current_end = int(re.findall(r"20\d{2}", historical.name)[-1])
                candidate_end = int(years[-1])
                if candidate_end > current_end:
                    historical = path
        else:
            partials.append(path)

    if historical is None:
        partials = files

    def sort_key(path: Path) -> tuple[int, int]:
        years = re.findall(r"20\d{2}", path.name)
        max_year = max((int(year) for year in years), default=0)
        return max_year, get_month_value(path.name)

    current = max(partials, key=sort_key) if partials else None
    return historical, current


def detectar_archivos() -> tuple[Path | None, Path | None]:
    """Devuelve las fuentes canonicas o, durante la migracion, las legadas."""

    canonical_exists = {key: path.exists() for key, path in CANONICAL_SOURCES.items()}
    if all(canonical_exists.values()):
        return CANONICAL_SOURCES["historico"], CANONICAL_SOURCES["actual"]
    if any(canonical_exists.values()):
        missing = [key for key, exists in canonical_exists.items() if not exists]
        raise FileNotFoundError(
            "Migracion de fuentes incompleta; faltan archivos canonicos: " + ", ".join(missing)
        )
    return _detectar_archivos_legados()


def _source_years(frame: pd.DataFrame, source_name: str) -> set[int]:
    normalized = {str(column).lower().strip().replace(" ", "_"): column for column in frame.columns}
    date_column = normalized.get("fecha_infraccion")
    if date_column is None:
        raise ValueError(f"La fuente {source_name} no contiene FECHA_INFRACCION")
    dates = pd.to_datetime(frame[date_column], errors="coerce")
    if dates.notna().sum() == 0:
        raise ValueError(f"La fuente {source_name} no contiene fechas validas")
    return {int(year) for year in dates.dt.year.dropna().unique()}


def consolidar() -> bool:
    """Ejecuta la consolidacion, los invariantes y la limpieza."""

    try:
        historical_path, current_path = detectar_archivos()
        if not historical_path or not current_path:
            raise FileNotFoundError(
                "Se requieren una fuente historica y una fuente del anio en curso en data/raw"
            )

        print("=" * 60)
        print("CONSOLIDACION DE DATOS DE HOMICIDIOS")
        print("=" * 60)
        print(f"Historico: {historical_path.name}")
        print(f"Actual:    {current_path.name}")

        historical = smart_read_excel(historical_path, "Historico")
        current = smart_read_excel(current_path, "Anio en curso acumulado")
        if historical.empty or current.empty:
            raise ValueError("Una de las fuentes primarias no contiene registros")

        historical_years = _source_years(historical, historical_path.name)
        current_years = _source_years(current, current_path.name)
        overlap = historical_years & current_years
        if overlap:
            raise ValueError(
                "Las fuentes se solapan en los anios "
                + ", ".join(map(str, sorted(overlap)))
                + "; se detiene el pipeline para evitar duplicados"
            )

        print("\nUniendo registros...")
        print(f"  Historico: {len(historical):,}")
        print(f"  Actual:    {len(current):,}")
        consolidated = pd.concat([historical, current], ignore_index=True)
        print(f"  Total:     {len(consolidated):,}")

        DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
        temp_consolidated = OUTPUT_CONSOLIDATED.with_suffix(".csv.tmp")
        consolidated.to_csv(temp_consolidated, index=False)
        os.replace(temp_consolidated, OUTPUT_CONSOLIDATED)
        print(f"Archivo intermedio: {OUTPUT_CONSOLIDATED}")

        print("\n" + "=" * 60)
        print("LIMPIEZA DE DATOS")
        print("=" * 60)
        from scripts.limpiar_datos import clean_data

        if not clean_data(OUTPUT_CONSOLIDATED, OUTPUT_CLEAN):
            raise RuntimeError("La limpieza no pudo generar la salida final")
        return True
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return False


if __name__ == "__main__":
    raise SystemExit(0 if consolidar() else 1)
