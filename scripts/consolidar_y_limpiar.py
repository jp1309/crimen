"""
Consolidar y Limpiar Datos de Homicidios
========================================
Script principal del pipeline ETL que:
1. Detecta automáticamente el archivo Excel 2025 más reciente
2. Lo fusiona con el histórico 2014-2024
3. Ejecuta la limpieza de datos

Uso:
    python scripts/consolidar_y_limpiar.py
"""

import pandas as pd
import os
import sys

# Rutas del proyecto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW = os.path.join(PROJECT_ROOT, "data", "raw")
DATA_PROCESSED = os.path.join(PROJECT_ROOT, "data", "processed")
OUTPUT_CLEAN = os.path.join(PROJECT_ROOT, "homicidios_clean.csv")


def get_month_value(filename):
    """
    Determina el valor de ordenamiento de un archivo por su nombre.
    Archivos con 'enero' y 'diciembre' (año completo) tienen prioridad máxima.
    """
    meses_map = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
        'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }

    clean_name = filename.lower().replace(".xlsx", "")
    parts = clean_name.replace("_", " ").split()

    # Prioridad máxima: archivos que contengan "enero" Y "diciembre" (año completo)
    if 'enero' in parts and 'diciembre' in parts:
        return 13

    # Buscar nombre de mes explícito (tomar el más alto si hay varios)
    max_month = 0
    for part in parts:
        if part in meses_map and meses_map[part] > max_month:
            max_month = meses_map[part]
    if max_month > 0:
        return max_month

    # Si no hay nombre, buscar número (ej: 2025_11 -> 11)
    for part in parts:
        if part.isdigit():
            val = int(part)
            if 1 <= val <= 12:
                return val
    return 0


def smart_read_excel(path, desc):
    """
    Lee un archivo Excel buscando automáticamente la hoja y fila de encabezado correctas.
    Los archivos del MDI suelen tener hojas de presentación que hay que ignorar.
    """
    print(f"Leyendo {desc} ({os.path.basename(path)})...")

    if not os.path.exists(path):
        print(f"  Advertencia: Archivo no encontrado.")
        return pd.DataFrame()

    try:
        xls = pd.ExcelFile(path)
    except Exception as e:
        print(f"  Error abriendo Excel: {e}")
        return pd.DataFrame()

    target_sheet = None
    header_row = -1

    # Recorrer hojas buscando PROVINCIA
    for sheet in xls.sheet_names:
        try:
            df_preview = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=50)
        except:
            continue

        for i, row in df_preview.iterrows():
            row_str = " ".join([str(x).upper() if pd.notna(x) else "" for x in row.values])

            # Criterios: PROVINCIA y (FECHA o ZONA o CANTON)
            if "PROVINCIA" in row_str and ("FECHA" in row_str or "ZONA" in row_str or "CANTON" in row_str):
                target_sheet = sheet
                header_row = i
                print(f"  -> Datos en hoja '{sheet}', encabezado fila {i}")
                break
        if target_sheet:
            break

    if not target_sheet:
        print(f"  Error: No se detectó tabla de datos válida.")
        return pd.DataFrame()

    try:
        df = pd.read_excel(xls, sheet_name=target_sheet, header=header_row)
        return df
    except Exception as e:
        print(f"  Error leyendo datos: {e}")
        return pd.DataFrame()


def consolidar():
    """Función principal de consolidación."""

    # Detectar archivos Excel 2025 en data/raw
    archivos = [f for f in os.listdir(DATA_RAW)
                if "2025" in f and f.endswith(".xlsx") and not f.startswith("~$")]

    if not archivos:
        print("Error: No se encontró ningún archivo Excel de 2025 en data/raw/")
        return False

    # Seleccionar el archivo más completo
    archivo_nuevo_2025 = max(archivos, key=get_month_value)
    archivo_historico = "mdi_homicidios_intencionales_pm_2014_2024.xlsx"

    print("=" * 50)
    print("CONSOLIDACIÓN DE DATOS DE HOMICIDIOS")
    print("=" * 50)
    print(f"Histórico: {archivo_historico}")
    print(f"Datos 2025: {archivo_nuevo_2025}")
    print()

    try:
        # 1. Cargar histórico
        df_hist = smart_read_excel(
            os.path.join(DATA_RAW, archivo_historico),
            "Histórico 2014-2024"
        )

        # 2. Cargar nuevo archivo 2025
        df_2025 = smart_read_excel(
            os.path.join(DATA_RAW, archivo_nuevo_2025),
            "Datos 2025"
        )

        if df_hist.empty and df_2025.empty:
            print("Error: No hay datos para procesar.")
            return False

        # 3. Consolidar
        print(f"\nUniendo registros...")
        print(f"  Histórico: {len(df_hist):,} registros")
        print(f"  2025:      {len(df_2025):,} registros")

        df_consolidado = pd.concat([df_hist, df_2025], ignore_index=True)
        print(f"  Total:     {len(df_consolidado):,} registros")

        # Guardar archivo intermedio
        output_consolidado = os.path.join(DATA_PROCESSED, "homicidios_consolidado.csv")
        df_consolidado.to_csv(output_consolidado, index=False)
        print(f"\nArchivo intermedio: {output_consolidado}")

        # 4. Ejecutar limpieza
        print("\n" + "=" * 50)
        print("LIMPIEZA DE DATOS")
        print("=" * 50)

        from scripts import limpiar_datos
        limpiar_datos.clean_data(output_consolidado, OUTPUT_CLEAN)

        return True

    except Exception as e:
        print(f"Error crítico: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = consolidar()
    sys.exit(0 if success else 1)
