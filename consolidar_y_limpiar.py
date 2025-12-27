import pandas as pd
import os
import sys

def consolidar():
    # Detectar el archivo 2025 más reciente en la carpeta
    archivos = [f for f in os.listdir('.') if f.startswith("mdi_homicidiosintencionalse_pm_2025") and f.endswith(".xlsx")]
    if not archivos:
        print("❌ Error: No se encontró ningún archivo Excel de 2025.")
        return
    
    # Tomar el más reciente (alfabéticamente noviembre > octubre)
    archivo_nuevo_2025 = sorted(archivos)[-1]
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
            print("❌ Error: No se encontró el encabezado 'Provincia' en el archivo 2025.")
            return

        df_2025 = pd.read_excel(archivo_nuevo_2025, header=header_row)
        
        # 3. Consolidar
        print(f"Uniendo registros ({len(df_hist)} + {len(df_2025)})...")
        df_consolidado = pd.concat([df_hist, df_2025], ignore_index=True)
        
        output_consolidado = "homicidios_consolidado.csv"
        df_consolidado.to_csv(output_consolidado, index=False)
        print(f"✅ Archivo {output_consolidado} generado.")
        
        # 4. Lanzar limpieza
        print("\n--- Ejecutando Limpieza (inspect_excel.py) ---")
        import inspect_excel
        inspect_excel.clean_data()
        
    except Exception as e:
        print(f"❌ Error durante el proceso: {e}")

if __name__ == "__main__":
    consolidar()
