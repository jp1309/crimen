"""
Verificar Duplicados de Cantones
================================
Detecta posibles duplicados en nombres de cantones
causados por variantes ortográficas o tildes.

Uso:
    python scripts/verificar_cantones.py
"""

import pandas as pd
import unidecode
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_FILE = os.path.join(PROJECT_ROOT, "homicidios_clean.csv")


def inspect_cantons():
    """Busca duplicados de cantones por variantes ortográficas."""

    if not os.path.exists(CLEAN_FILE):
        print(f"Error: {CLEAN_FILE} no encontrado")
        return

    print("Cargando datos...")
    df = pd.read_csv(CLEAN_FILE, low_memory=False)

    provinces = sorted(df['provincia'].dropna().unique())

    print("\n" + "=" * 50)
    print("VERIFICACIÓN DE DUPLICADOS EN CANTONES")
    print("=" * 50)

    found_issues = False

    for prov in provinces:
        cantons = sorted(df[df['provincia'] == prov]['canton'].dropna().unique())

        # Comparar versiones normalizadas
        seen = {}
        for canton in cantons:
            normalized = unidecode.unidecode(canton)
            if normalized in seen:
                if not found_issues:
                    print("\nDuplicados encontrados:\n")
                print(f"  {prov}: '{seen[normalized]}' vs '{canton}'")
                found_issues = True
            else:
                seen[normalized] = canton

    if not found_issues:
        print("\n[OK] No se encontraron duplicados por tildes/ortografia")
    else:
        print("\nRecomendación: Agregar mapeo al script de limpieza")


if __name__ == "__main__":
    inspect_cantons()
