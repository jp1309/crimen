import pandas as pd
import os
import sys

def consolidar():
    # Detectar el archivo 2025 más reciente en la carpeta
    archivos = [f for f in os.listdir('.') if f.startswith("mdi_homicidiosintencionalse_pm_2025") and f.endswith(".xlsx")]
    if not archivos:
        print("Error: No se encontró ningún archivo Excel de 2025.")
        return
    
    # Mapeo de meses para ordenamiento correcto
    meses_map = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
        'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }

    def get_month_value(filename):
        # El nombre suele terminar en ...enero_noviembre.xlsx" o "...octubre.xlsx"
        # Buscamos la última palabra antes del .xlsx
        clean_name = filename.lower().replace(".xlsx", "")
        parts = clean_name.split("_")
        last_part = parts[-1]
        return meses_map.get(last_part, 0)

    # Tomar el que tenga el mes más alto
    archivo_nuevo_2025 = max(archivos, key=get_month_value)
    archivo_historico = "mdi_homicidios_intencionales_pm_2014_2024.xlsx"
    
    print(f"--- Iniciando Consolidación ---")
    print(f"Histórico: {archivo_historico}")
    print(f"Nuevo: {archivo_nuevo_2025}")
    
    try:
        # 1. Cargar histórico
        print("Leyendo histórico...")
        df_hist = pd.read_excel(archivo_historico)
        
        # 2. Cargar nuevo archivo 2025 (buscando encabezado)
        print("Leyendo datos 2025...")
        df_raw = pd.read_excel(archivo_nuevo_2025, header=None)
        header_row = -1
        for i, row in df_raw.head(30).iterrows():
            if "Provincia" in str(row.values).upper():
                header_row = i
                break
        
        if header_row == -1:
            print("Error: No se encontró el encabezado 'Provincia' en el archivo 2025.")
            return

        df_2025 = pd.read_excel(archivo_nuevo_2025, header=header_row)
        
        # 3. Consolidar
        print(f"Uniendo registros ({len(df_hist)} + {len(df_2025)})...")
        df_consolidado = pd.concat([df_hist, df_2025], ignore_index=True)
        
        output_consolidado = "homicidios_consolidado.csv"
        df_consolidado.to_csv(output_consolidado, index=False)
        print(f"Archivo {output_consolidado} generado.")
        
        # 4. Lanzar limpieza
        print("\n--- Ejecutando Limpieza (inspect_excel.py) ---")
        import inspect_excel
        inspect_excel.clean_data()
        
    except Exception as e:
        print(f"Error durante el proceso: {e}")

if __name__ == "__main__":
    consolidar()
