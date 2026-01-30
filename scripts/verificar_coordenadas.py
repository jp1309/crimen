"""
Verificar Completitud de Coordenadas
====================================
Calcula el porcentaje de registros con coordenadas
geográficas válidas por año.

Uso:
    python scripts/verificar_coordenadas.py
"""

import pandas as pd
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_FILE = os.path.join(PROJECT_ROOT, "homicidios_clean.csv")


def check_coords():
    """Verifica la completitud de coordenadas por año."""

    if not os.path.exists(CLEAN_FILE):
        print(f"Error: {CLEAN_FILE} no encontrado")
        return

    print("Cargando datos...")
    df = pd.read_csv(CLEAN_FILE)

    df['coordenada_x'] = pd.to_numeric(df['coordenada_x'], errors='coerce')
    df['coordenada_y'] = pd.to_numeric(df['coordenada_y'], errors='coerce')

    years = sorted(df['anio'].unique())

    print(f"\n{'AÑO':<6} | {'TOTAL':>8} | {'CON COORD':>10} | {'COMPLETITUD':>12}")
    print("-" * 45)

    for year in years:
        subset = df[df['anio'] == year]
        total = len(subset)

        # Coordenadas válidas: no nulas y distintas de 0
        valid = subset[
            (subset['coordenada_x'].notna()) &
            (subset['coordenada_y'].notna()) &
            (subset['coordenada_x'] != 0) &
            (subset['coordenada_y'] != 0)
        ]

        count_valid = len(valid)
        pct = (count_valid / total) * 100 if total > 0 else 0

        print(f"{int(year):<6} | {total:>8,} | {count_valid:>10,} | {pct:>10.1f}%")

    # Resumen total
    total_all = len(df)
    valid_all = len(df[
        (df['coordenada_x'].notna()) &
        (df['coordenada_y'].notna()) &
        (df['coordenada_x'] != 0) &
        (df['coordenada_y'] != 0)
    ])
    pct_all = (valid_all / total_all) * 100

    print("-" * 45)
    print(f"{'TOTAL':<6} | {total_all:>8,} | {valid_all:>10,} | {pct_all:>10.1f}%")


if __name__ == "__main__":
    check_coords()
