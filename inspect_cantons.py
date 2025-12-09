import pandas as pd
import unidecode

def normalize_text(text):
    if pd.isna(text):
        return text
    # Uppercase and strip
    text = str(text).upper().strip()
    return text

def inspect_cantons():
    file_path = "homicidios_clean.csv"
    print(f"Loading {file_path}...")
    df = pd.read_csv(file_path, low_memory=False)

    # Group by Province and list unique Cantons
    provinces = sorted(df['provincia'].dropna().unique())

    print("\n--- POSIBLES DUPLICADOS POR TILDE/ESCRITURA ---\n")
    
    found_issues = False
    
    for prov in provinces:
        cantons = sorted(df[df['provincia'] == prov]['canton'].dropna().unique())
        
        # Simple check: compare normalized versions
        seen_normalized = {}
        for c in cantons:
            norm = unidecode.unidecode(c) # removed accents
            if norm in seen_normalized:
                print(f"PROVINCIA: {prov}")
                print(f"  Conflict: '{seen_normalized[norm]}' vs '{c}'")
                found_issues = True
            else:
                seen_normalized[norm] = c

    if not found_issues:
        print("No obvious accent-based duplicates found with this method.")
    else:
        print("\nRecomendación: Normalizar quitando tildes en el script de limpieza.")

if __name__ == "__main__":
    inspect_cantons()
