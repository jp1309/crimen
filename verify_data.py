import pandas as pd
import os

def verify_data_integrity():
    print("--- Verifying Data Integrity ---\n")
    
    # 1. Load Raw Sources
    path_2014_2024 = "mdi_homicidios_intencionales_pm_2014_2024.xlsx"
    path_2025 = "mdi_homicidiosintencionalse_pm_2025_enero_noviembre.xlsx"
    path_clean = "homicidios_clean.csv"

    # Count 2014-2024
    count_historic = 0
    if os.path.exists(path_2014_2024):
        print(f"Reading {path_2014_2024}...")
        # Usually data is in the first sheet or specific sheet, let's check all just in case or assume first
        try:
            xls = pd.ExcelFile(path_2014_2024)
            # Assuming data is in the sheet with most rows or 'General'
            # Based on previous inspection, there was a sheet named 'MDI...' or similar.
            # We'll valid rows by checking a mandatory column like 'Provincia' or 'Fecha'
            for sheet in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet)
                # Naive check: valid rows usually have a date
                if 'Fecha Infraccion' in df.columns or 'fecha_infraccion' in df.columns or 'Fecha' in df.columns:
                     # Attempt to find the column name that matches
                    col = next(c for c in df.columns if 'fecha' in str(c).lower())
                    rows = df[col].notna().sum()
                    print(f"  Sheet '{sheet}': {rows} valid rows")
                    count_historic += rows
                else:
                    # Maybe it has a header offset?
                    # Let's try reading skipping header rows like we did in inspection
                     df = pd.read_excel(xls, sheet_name=sheet, header=None)
                     # Look for "Zona" or "Provincia"
                     start_idx = -1
                     for i, r in df.head(20).iterrows():
                         row_str = " ".join([str(x) for x in r.values])
                         if "Provincia" in row_str:
                             start_idx = i
                             break
                     
                     if start_idx != -1:
                        df = pd.read_excel(xls, sheet_name=sheet, header=start_idx)
                        rows = len(df)
                        print(f"  Sheet '{sheet}' (detected header at {start_idx}): {rows} rows")
                        count_historic += rows
                     else:
                        print(f"  Sheet '{sheet}': Could not identify data table.")
        except Exception as e:
            print(f"Error reading historic file: {e}")
    else:
        print("Warning: Historic Excel file not found.")

    # Count 2025
    count_2025 = 0
    if os.path.exists(path_2025):
        print(f"\nReading {path_2025}...")
        try:
            # Inspection showed data starts around row 16-17 probably, let's use the same logic
            df_raw = pd.read_excel(path_2025, header=None)
            header_row = -1
            for i, row in df_raw.head(30).iterrows():
                if "Provincia" in str(row.values) or "PROVINCIA" in str(row.values):
                    header_row = i
                    break
            
            if header_row != -1:
                df = pd.read_excel(path_2025, header=header_row)
                count_2025 = len(df)
                print(f"  File 2025: {count_2025} rows (Head at row {header_row})")
            else:
                 print("  Could not find header in 2025 file.")
        except Exception as e:
            print(f"Error reading 2025 file: {e}")
    
    total_expected = count_historic + count_2025
    print(f"\nTotal Expected Rows (Raw Sum): {total_expected}")

    # 2. Check Cleaned CSV
    print(f"\nChecking {path_clean}...")
    if os.path.exists(path_clean):
        df_clean = pd.read_csv(path_clean)
        print(f"  Clean Data Rows: {len(df_clean)}")
        
        # Breakdown by year
        print("\nBreakdown by Year in Clean Data:")
        counts_by_year = df_clean['anio'].value_counts().sort_index()
        print(counts_by_year)
        
        print(f"\nDifference: {len(df_clean) - total_expected}")
        if abs(len(df_clean) - total_expected) < 50:
            print(">> SUCCESS: Data counts match closely.")
        else:
            print(">> WARNING: Significant discrepancy in row counts.")
    else:
        print("Clean file not found.")

if __name__ == "__main__":
    verify_data_integrity()
