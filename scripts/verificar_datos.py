"""Verifica que el CSV limpio reproduzca exactamente las fuentes primarias."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from scripts.configuracion import OUTPUT_CLEAN
from scripts.consolidar_y_limpiar import detectar_archivos, smart_read_excel


def _year_counts(frame: pd.DataFrame, source_name: str) -> dict[int, int]:
    normalized = {str(column).lower().strip().replace(" ", "_"): column for column in frame.columns}
    if "fecha_infraccion" not in normalized:
        raise ValueError(f"{source_name} no contiene FECHA_INFRACCION")
    dates = pd.to_datetime(frame[normalized["fecha_infraccion"]], errors="coerce")
    invalid = int(dates.isna().sum())
    if invalid:
        raise ValueError(f"{source_name} contiene {invalid:,} fechas invalidas")
    return {int(year): int(count) for year, count in dates.dt.year.value_counts().items()}


def verify_data_integrity(clean_file: str | Path = OUTPUT_CLEAN) -> bool:
    print("=" * 60)
    print("VERIFICACION DE INTEGRIDAD DE DATOS")
    print("=" * 60)

    try:
        historical_path, current_path = detectar_archivos()
        if not historical_path or not current_path:
            raise FileNotFoundError("No se detectaron las dos fuentes primarias")

        sources = [
            smart_read_excel(historical_path, "Historico"),
            smart_read_excel(current_path, "Anio en curso acumulado"),
        ]
        expected_count = sum(len(frame) for frame in sources)
        expected_years: dict[int, int] = {}
        for frame, path in zip(sources, (historical_path, current_path)):
            for year, count in _year_counts(frame, path.name).items():
                if year in expected_years:
                    raise ValueError(f"El anio {year} aparece en mas de una fuente")
                expected_years[year] = count

        clean_path = Path(clean_file)
        if not clean_path.exists():
            raise FileNotFoundError(f"CSV limpio no encontrado: {clean_path}")
        clean = pd.read_csv(clean_path, low_memory=False)
        if "anio" not in clean.columns:
            raise ValueError("El CSV limpio no contiene la columna anio")
        clean_years = {
            int(year): int(count)
            for year, count in clean["anio"].value_counts(dropna=False).items()
            if pd.notna(year)
        }

        print(f"\nRegistros esperados: {expected_count:,}")
        print(f"Registros en CSV:    {len(clean):,}")
        print("\nDesglose por anio:")
        all_years = sorted(set(expected_years) | set(clean_years))
        for year in all_years:
            expected = expected_years.get(year, 0)
            actual = clean_years.get(year, 0)
            marker = "OK" if expected == actual else "ERROR"
            print(f"  {year}: fuente={expected:>7,} csv={actual:>7,} [{marker}]")

        valid = expected_count == len(clean) and expected_years == clean_years
        if valid:
            print("\n[OK] VERIFICACION EXACTA EXITOSA")
        else:
            print("\n[ERROR] El CSV no reproduce exactamente las fuentes")
        return valid
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return False


if __name__ == "__main__":
    raise SystemExit(0 if verify_data_integrity() else 1)
