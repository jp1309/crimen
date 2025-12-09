import pandas as pd
import os

def check_coords():
    file_path = "homicidios_clean.csv"
    if not os.path.exists(file_path):
        print(f"File {file_path} not found.")
        return

    print("Loading data...")
    df = pd.read_csv(file_path)

    # Convert coordinates to numeric, coercing errors
    df['coordenada_x'] = pd.to_numeric(df['coordenada_x'], errors='coerce')
    df['coordenada_y'] = pd.to_numeric(df['coordenada_y'], errors='coerce')

    # Group by Year
    results = []
    years = sorted(df['anio'].unique())

    print(f"\n{'AÑO':<6} | {'TOTAL':>8} | {'CON COORD':>10} | {'% COMPLETITUD':>12}")
    print("-" * 45)

    for year in years:
        subset = df[df['anio'] == year]
        total = len(subset)
        
        # Check for valid lat/lon (not null and usually not exactly 0 unless on equator/prime meridian, 
        # but 0,0 is off Africa, so unlikely relevant for Ecuador)
        # Ecuador is roughly Lat -1.8, Lon -78. Let's strictly check non-null first.
        valid_coords = subset[
            (subset['coordenada_x'].notna()) & 
            (subset['coordenada_y'].notna()) &
            (subset['coordenada_x'] != 0) & 
            (subset['coordenada_y'] != 0)
        ]
        
        count_valid = len(valid_coords)
        pct = (count_valid / total) * 100 if total > 0 else 0
        
        results.append({
            'Year': year, 
            'Total': total, 
            'Valid': count_valid, 
            'Pct': pct
        })

        print(f"{year:<6} | {total:>8} | {count_valid:>10} | {pct:>11.1f}%")

if __name__ == "__main__":
    check_coords()
