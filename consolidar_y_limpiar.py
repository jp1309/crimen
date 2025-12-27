import pandas as pd
import os
import sys

def consolidar():
    # Detectar archivos Excel que contengan "2025" en el nombre (excluyendo temporales ~$)
    archivos = [f for f in os.listdir('.') if "2025" in f and f.endswith(".xlsx") and not f.startswith("~$")]
    if not archivos:
        print("Error: No se encontró ningún archivo Excel de 2025.")
        return
    
    # Mapeo de meses para ordenamiento correcto
    meses_map = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
        'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }

    def get_month_value(filename):
        # Intentar extraer mes del nombre
        clean_name = filename.lower().replace(".xlsx", "")
        parts = clean_name.replace("_", " ").split() 
        
        # Buscar nombre de mes explícito
        for part in parts:
            if part in meses_map:
                return meses_map[part]
        
        # Si no hay nombre, buscar número (ej: 2025_11 -> 11)
        candidate_month = 0
        for part in parts:
            if part.isdigit():
                val = int(part)
                if 1 <= val <= 12:
                    candidate_month = val
        return candidate_month

    # Tomar el que tenga el mes más alto
    archivo_nuevo_2025 = max(archivos, key=get_month_value)
    archivo_historico = "mdi_homicidios_intencionales_pm_2014_2024.xlsx"
    
    print(f"--- Iniciando Consolidación ---")
    print(f"Histórico: {archivo_historico}")
    print(f"Nuevo (detectado): {archivo_nuevo_2025}")
    
    def smart_read_excel(path, desc):
        print(f"Leyendo {desc} ({path})...")
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
                # Convert to string/upper safely
                row_str = " ".join([str(x).upper() if pd.notna(x) else "" for x in row.values])
                
                # Criterios: PROVINCIA y (FECHA o ZONA o CANTON)
                if "PROVINCIA" in row_str and ("FECHA" in row_str or "ZONA" in row_str or "CANTON" in row_str):
                    target_sheet = sheet
                    header_row = i
                    print(f"  -> Datos encontrados en hoja '{sheet}', fila encabezado {i}")
                    break
            if target_sheet:
                break
        
        if not target_sheet:
            print(f"  Error: No se detectó tabla de datos válida en {desc}.")
            return pd.DataFrame()
            
        try:
            df = pd.read_excel(xls, sheet_name=target_sheet, header=header_row)
            return df
        except Exception as e:
            print(f"  Error leyendo datos: {e}")
            return pd.DataFrame()

    try:
        # 1. Cargar histórico
        df_hist = smart_read_excel(archivo_historico, "Histórico")
        
        # 2. Cargar nuevo archivo 2025
        df_2025 = smart_read_excel(archivo_nuevo_2025, "Datos 2025")
        
        if df_hist.empty and df_2025.empty:
            print("Error: No hay datos para procesar (ambos DataFrames vacíos).")
            return

        # 3. Consolidar
        print(f"Uniendo registros (Histórico: {len(df_hist)} + Nuevo: {len(df_2025)})...")
        # Asegurar columnas consistentes si es necesario (el concat lo maneja por nombre)
        df_consolidado = pd.concat([df_hist, df_2025], ignore_index=True)
        
        output_consolidado = "homicidios_consolidado.csv"
        df_consolidado.to_csv(output_consolidado, index=False)
        print(f"Archivo intermedio {output_consolidado} generado.")
        
        # 4. Lanzar limpieza
        print("\n--- Ejecutando Limpieza (inspect_excel.py) ---")
        import inspect_excel
        inspect_excel.clean_data()
        
    except Exception as e:
        print(f"Error crítico durante el proceso: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    consolidar()
