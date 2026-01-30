"""
Verificar Integridad de Datos
=============================
Script de QA que compara el conteo de registros entre
los archivos Excel fuente y el CSV limpio final.

Uso:
    python scripts/verificar_datos.py
"""

import pandas as pd
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW = os.path.join(PROJECT_ROOT, "data", "raw")
CLEAN_FILE = os.path.join(PROJECT_ROOT, "homicidios_clean.csv")


def verify_data_integrity():
    """Verifica la integridad de los datos comparando fuentes con salida."""

    print("=" * 50)
    print("VERIFICACIÓN DE INTEGRIDAD DE DATOS")
    print("=" * 50)

    # 1. Contar registros del histórico
    path_historic = os.path.join(DATA_RAW, "mdi_homicidios_intencionales_pm_2014_2024.xlsx")
    count_historic = 0

    if os.path.exists(path_historic):
        print(f"\nLeyendo histórico...")
        try:
            xls = pd.ExcelFile(path_historic)
            for sheet in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet, header=None)
                # Buscar fila de encabezado
                for i, row in df.head(20).iterrows():
                    if "Provincia" in str(row.values) or "PROVINCIA" in str(row.values):
                        df = pd.read_excel(xls, sheet_name=sheet, header=i)
                        count_historic = len(df)
                        print(f"  Histórico 2014-2024: {count_historic:,} registros")
                        break
                if count_historic > 0:
                    break
        except Exception as e:
            print(f"  Error: {e}")
    else:
        print("  Advertencia: Archivo histórico no encontrado")

    # 2. Contar registros del archivo 2025
    archivos_2025 = [f for f in os.listdir(DATA_RAW)
                     if "2025" in f and f.endswith(".xlsx") and not f.startswith("~$")]
    count_2025 = 0

    if archivos_2025:
        path_2025 = os.path.join(DATA_RAW, archivos_2025[0])
        print(f"\nLeyendo {archivos_2025[0]}...")
        try:
            df_raw = pd.read_excel(path_2025, header=None)
            for i, row in df_raw.head(30).iterrows():
                if "Provincia" in str(row.values) or "PROVINCIA" in str(row.values):
                    df = pd.read_excel(path_2025, header=i)
                    count_2025 = len(df)
                    print(f"  Datos 2025: {count_2025:,} registros")
                    break
        except Exception as e:
            print(f"  Error: {e}")

    total_expected = count_historic + count_2025
    print(f"\nTotal esperado: {total_expected:,}")

    # 3. Verificar CSV limpio
    print(f"\n" + "-" * 50)
    if os.path.exists(CLEAN_FILE):
        df_clean = pd.read_csv(CLEAN_FILE)
        print(f"CSV limpio: {len(df_clean):,} registros")

        # Desglose por año
        print("\nDesglose por año:")
        counts = df_clean['anio'].value_counts().sort_index()
        for year, count in counts.items():
            print(f"  {int(year)}: {count:,}")

        diff = len(df_clean) - total_expected
        print(f"\nDiferencia: {diff:+,}")

        if abs(diff) < 50:
            print("\n[OK] VERIFICACION EXITOSA")
        else:
            print("\n[!] ADVERTENCIA: Discrepancia significativa")
    else:
        print("Error: CSV limpio no encontrado")


if __name__ == "__main__":
    verify_data_integrity()
