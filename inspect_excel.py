import pandas as pd
import numpy as np
import os
import unidecode

def clean_data():
    file_path = "homicidios_consolidado.csv"
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    print(f"Loading {file_path}...")
    df = pd.read_csv(file_path, low_memory=False)

    print(f"Original shape: {df.shape}")

    # 1. Drop artifact columns
    drop_cols = [c for c in df.columns if "unnamed" in c.lower()]
    if drop_cols:
        print(f"Dropping columns: {drop_cols}")
        df = df.drop(columns=drop_cols)

    # 2. Standardize column names
    df.columns = [c.lower().strip().replace(" ", "_") for c in df.columns]

    # 3. Handle Dates
    print("Processing dates...")
    df['fecha_infraccion'] = pd.to_datetime(df['fecha_infraccion'], errors='coerce')
    
    # Create derived date columns for easier filtering
    df['anio'] = df['fecha_infraccion'].dt.year
    df['mes'] = df['fecha_infraccion'].dt.month
    df['dia_semana'] = df['fecha_infraccion'].dt.day_name(locale='es_ES') if 'day_name' in dir(df['fecha_infraccion'].dt) else df['fecha_infraccion'].dt.dayofweek

    # 4. Handle Numeric - Age
    print("Processing numeric values (Eat, Coords)...")
    # 'edad' might contain non-numeric chars
    df['edad'] = pd.to_numeric(df['edad'], errors='coerce')

    # 5. Handle Coordinates (Fix comma/dot decimal issues)
    for col in ['coordenada_x', 'coordenada_y']:
        if col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 6. Standardize Text
    text_cols = ['provincia', 'canton', 'parroquia', 'sexo', 'estado_civil', 
                 'nacionalidad', 'tipo_muerte', 'arma', 'tipo_lugar', 'zona']
    
    for col in text_cols:
        if col in df.columns:
            # Uppercase, strip, and remove accents
            df[col] = df[col].astype(str).str.upper().str.strip()
            df[col] = df[col].apply(lambda x: unidecode.unidecode(x) if pd.notnull(x) else x)
            # Unify common missing values
            df[col] = df[col].replace(['SIN_DATO', 'NO DETERMINADO', 'NAN'], 'DESCONOCIDO')

    # 6.5 Normalize Canton Names (Standardize different spellings)
    print("Normalizing canton names...")
    if 'canton' in df.columns:
        canton_mapping = {
            # Guayas
            'ALFREDO BAQUERIZO MORENO (JUJAN)': 'ALFREDO BAQUERIZO MORENO',
            'CRNEL. MARCELINO MARIDUENA': 'CORONEL MARCELINO MARIDUENA',
            'GNRAL. ANTONIO ELIZALDE': 'GENERAL ANTONIO ELIZALDE',
        }
        
        df['canton'] = df['canton'].replace(canton_mapping)
        
        # Report changes
        unique_cantons = df[df['provincia'] == 'GUAYAS']['canton'].unique()
        print(f"Unique cantons in GUAYAS after normalization: {len(unique_cantons)}")


    # 7. Add categorization logic (Example: Rango de Edad)
    bins = [0, 12, 18, 30, 50, 65, 100]
    labels = ['Niño', 'Adolescente', 'Joven', 'Adulto', 'Adulto Mayor', 'Anciano']
    df['rango_edad'] = pd.cut(df['edad'], bins=bins, labels=labels, right=False)

    print("\nData Info after cleaning:")
    print(df.info())
    
    print("\nMissing values summary:")
    print(df.isnull().sum()[df.isnull().sum() > 0])

    # Save
    output_path = "homicidios_clean.csv"
    df.to_csv(output_path, index=False)
    print(f"\nSaved cleaned data to {output_path}")

if __name__ == "__main__":
    clean_data()
