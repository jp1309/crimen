"""
Limpiar Datos de Homicidios
===========================
Módulo de limpieza ETL que:
- Normaliza columnas y nombres
- Procesa fechas y coordenadas
- Estandariza texto (mayúsculas, sin tildes)
- Categoriza rangos de edad

Uso:
    Llamado automáticamente desde consolidar_y_limpiar.py
    O directamente: python scripts/limpiar_datos.py
"""

import pandas as pd
import numpy as np
import os
import unidecode


def clean_data(input_path, output_path):
    """
    Limpia y normaliza los datos del CSV consolidado.

    Args:
        input_path: Ruta al archivo CSV de entrada
        output_path: Ruta donde guardar el CSV limpio
    """
    if not os.path.exists(input_path):
        print(f"Error: Archivo no encontrado: {input_path}")
        return False

    print(f"Cargando {os.path.basename(input_path)}...")
    df = pd.read_csv(input_path, low_memory=False)
    print(f"Registros originales: {len(df):,}")

    # 1. Eliminar columnas residuales
    drop_cols = [c for c in df.columns if "unnamed" in c.lower()]
    if drop_cols:
        print(f"Eliminando columnas: {drop_cols}")
        df = df.drop(columns=drop_cols)

    # 2. Normalizar nombres de columnas
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    # 3. Procesar fechas
    print("Procesando fechas...")
    df['fecha_infraccion'] = pd.to_datetime(df['fecha_infraccion'], errors='coerce')
    df['anio'] = df['fecha_infraccion'].dt.year
    df['mes'] = df['fecha_infraccion'].dt.month

    # Mapear día de la semana a español (sin depender de locale del sistema)
    dias_es = {
        'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miercoles',
        'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sabado', 'Sunday': 'Domingo'
    }
    df['dia_semana'] = df['fecha_infraccion'].dt.day_name().map(dias_es)

    # 4. Procesar edad (puede contener texto)
    print("Procesando valores numéricos...")
    df['edad'] = pd.to_numeric(df['edad'], errors='coerce')

    # 5. Corregir coordenadas (coma -> punto decimal)
    for col in ['coordenada_x', 'coordenada_y']:
        if col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 6. Normalizar texto
    print("Normalizando texto...")
    text_cols = ['provincia', 'canton', 'parroquia', 'sexo', 'estado_civil',
                 'nacionalidad', 'tipo_muerte', 'arma', 'tipo_lugar', 'zona']

    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.upper().str.strip()
            df[col] = df[col].apply(lambda x: unidecode.unidecode(x) if pd.notnull(x) else x)
            df[col] = df[col].replace(['SIN_DATO', 'NO DETERMINADO', 'NAN'], 'DESCONOCIDO')

    # 7. Normalizar nombres de cantones (variantes conocidas)
    print("Normalizando nombres de cantones...")
    if 'canton' in df.columns:
        canton_mapping = {
            'ALFREDO BAQUERIZO MORENO (JUJAN)': 'ALFREDO BAQUERIZO MORENO',
            'CRNEL. MARCELINO MARIDUENA': 'CORONEL MARCELINO MARIDUENA',
            'GNRAL. ANTONIO ELIZALDE': 'GENERAL ANTONIO ELIZALDE',
        }
        df['canton'] = df['canton'].replace(canton_mapping)

    # 8. Categorizar rangos de edad
    bins = [0, 12, 18, 30, 50, 65, 100]
    labels = ['Niño', 'Adolescente', 'Joven', 'Adulto', 'Adulto Mayor', 'Anciano']
    df['rango_edad'] = pd.cut(df['edad'], bins=bins, labels=labels, right=False)

    # Resumen
    print(f"\nRegistros finales: {len(df):,}")
    print(f"Columnas: {len(df.columns)}")

    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if len(missing) > 0:
        print(f"\nValores faltantes:")
        for col, count in missing.items():
            pct = count / len(df) * 100
            print(f"  {col}: {count:,} ({pct:.1f}%)")

    # Guardar
    df.to_csv(output_path, index=False)
    print(f"\nGuardado: {output_path}")
    return True


if __name__ == "__main__":
    # Ejecutar standalone (para pruebas)
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(PROJECT_ROOT, "data", "processed", "homicidios_consolidado.csv")
    output_file = os.path.join(PROJECT_ROOT, "homicidios_clean.csv")
    clean_data(input_file, output_file)
