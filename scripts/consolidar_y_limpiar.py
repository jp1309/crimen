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


def detectar_archivos():
    """
    Detecta automáticamente el histórico y el archivo más reciente en data/raw.
    - Histórico: archivo que cubre el rango más largo (detectado por tener dos años en el nombre, ej: 2014_2025)
    - Reciente: archivo con el año más alto y mes más completo
    """
    archivos = [f for f in os.listdir(DATA_RAW)
                if f.endswith(".xlsx") and not f.startswith("~$")]

    # Separar histórico (nombre con dos años distintos, ej: 2014_2025) de archivos anuales parciales
    import re
    historico = None
    parciales = []

    for f in archivos:
        años = re.findall(r'20\d{2}', f)
        if len(años) >= 2 and años[0] != años[-1]:
            # Tiene dos años distintos → es el histórico; quedarse con el de año final más alto
            if historico is None or int(re.findall(r'20\d{2}', f)[-1]) > int(re.findall(r'20\d{2}', historico)[-1]):
                historico = f
        else:
            parciales.append(f)

    # Si no hay histórico separado, usar todos los archivos como parciales
    if historico is None:
        parciales = archivos

    # Del resto, tomar el de año más reciente y mes más completo
    def sort_key(f):
        años = re.findall(r'20\d{2}', f)
        año_max = max(int(a) for a in años) if años else 0
        return (año_max, get_month_value(f))

    archivo_reciente = max(parciales, key=sort_key) if parciales else None

    return historico, archivo_reciente


def consolidar():
    """Función principal de consolidación."""

    historico, archivo_reciente = detectar_archivos()

    if not historico and not archivo_reciente:
        print("Error: No se encontró ningún archivo Excel en data/raw/")
        return False

    print("=" * 50)
    print("CONSOLIDACIÓN DE DATOS DE HOMICIDIOS")
    print("=" * 50)
    print(f"Histórico:  {historico or '(ninguno)'}")
    print(f"Reciente:   {archivo_reciente or '(ninguno)'}")
    print()

    try:
        # 1. Cargar histórico
        df_hist = smart_read_excel(
            os.path.join(DATA_RAW, historico),
            f"Histórico ({historico})"
        ) if historico else pd.DataFrame()

        # 2. Cargar archivo reciente (puede ser año en curso)
        df_reciente = smart_read_excel(
            os.path.join(DATA_RAW, archivo_reciente),
            f"Reciente ({archivo_reciente})"
        ) if archivo_reciente else pd.DataFrame()

        if df_hist.empty and df_reciente.empty:
            print("Error: No hay datos para procesar.")
            return False

        # 3. Consolidar
        print(f"\nUniendo registros...")
        print(f"  Histórico: {len(df_hist):,} registros")
        print(f"  Reciente:  {len(df_reciente):,} registros")

        df_consolidado = pd.concat([df_hist, df_reciente], ignore_index=True)
        print(f"  Total:     {len(df_consolidado):,} registros")

        # Guardar archivo intermedio
        output_consolidado = os.path.join(DATA_PROCESSED, "homicidios_consolidado.csv")
        df_consolidado.to_csv(output_consolidado, index=False)
        print(f"\nArchivo intermedio: {output_consolidado}")

        # 4. Ejecutar limpieza
        print("\n" + "=" * 50)
        print("LIMPIEZA DE DATOS")
        print("=" * 50)

        sys.path.insert(0, PROJECT_ROOT)
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
