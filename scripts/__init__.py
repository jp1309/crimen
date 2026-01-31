"""
Scripts del Pipeline ETL - Observatorio de Seguridad Ecuador
=============================================================

Este paquete contiene los scripts de procesamiento de datos para el
dashboard de homicidios intencionales en Ecuador (2014-2025).

Estructura del Pipeline
-----------------------
1. consolidar_y_limpiar.py  - Script principal (orquestador)
2. limpiar_datos.py         - Modulo de limpieza y normalizacion

Scripts de Validacion
---------------------
- verificar_datos.py        - Compara conteos Excel vs CSV
- verificar_coordenadas.py  - Reporta completitud geografica
- verificar_cantones.py     - Detecta duplicados ortograficos

Uso Basico
----------
    # Ejecutar pipeline completo
    python -m scripts.consolidar_y_limpiar

    # Verificar resultados
    python -m scripts.verificar_datos
    python -m scripts.verificar_coordenadas
    python -m scripts.verificar_cantones

Fuente de Datos
---------------
Ministerio del Interior de Ecuador (MDI)
- Historico: mdi_homicidios_intencionales_pm_2014_2024.xlsx
- Actual: mdi_homicidiosintencionalse_pm_2025_*.xlsx

Salida
------
- data/processed/homicidios_consolidado.csv  (intermedio)
- homicidios_clean.csv                       (produccion)
"""

from scripts.limpiar_datos import clean_data

__all__ = ['clean_data']
__version__ = '1.0.0'
