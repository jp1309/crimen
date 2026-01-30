# Observatorio de Seguridad - Ecuador

Dashboard interactivo para visualizar datos de homicidios intencionales en Ecuador (2014-2025).

**[Ver Dashboard](https://jp1309.github.io/crimen/)**

---

## Estructura del Proyecto

```
crimen/
├── index.html              # Dashboard principal
├── app.js                  # Lógica frontend (filtros, gráficos, mapa)
├── style.css               # Estilos personalizados
├── homicidios_clean.csv    # Datos limpios (producción)
│
├── data/
│   ├── raw/                # Archivos Excel fuente (MDI)
│   │   ├── mdi_homicidios_intencionales_pm_2014_2024.xlsx
│   │   └── mdi_homicidiosintencionalse_pm_2025_enero_diciembre.xlsx
│   └── processed/          # Archivos intermedios
│       └── homicidios_consolidado.csv
│
├── scripts/                # Pipeline ETL (Python)
│   ├── consolidar_y_limpiar.py   # Script principal
│   ├── limpiar_datos.py          # Módulo de limpieza
│   ├── verificar_datos.py        # Validación de integridad
│   ├── verificar_coordenadas.py  # Completitud de geolocalización
│   └── verificar_cantones.py     # Detección de duplicados
│
└── .github/workflows/
    └── update_data.yml     # CI/CD automático
```

---

## Vistas del Dashboard

| Vista | Descripción |
|-------|-------------|
| **Evolución** | Tendencias anuales/mensuales, tipos de arma, distribución horaria |
| **Ranking** | Pirámide demográfica, ranking por provincia/cantón |
| **Mapa** | Heatmap y marcadores geolocalizados |

---

## Tecnologías

**Frontend:** Vanilla JS, Chart.js, Leaflet.js, Tailwind CSS
**Backend (ETL):** Python 3.10+ (Pandas, Openpyxl, Unidecode)
**Deploy:** GitHub Pages + GitHub Actions

---

## Actualización de Datos

### Opción 1: Automática (GitHub Actions)

1. Colocar el nuevo archivo Excel en `data/raw/`
2. Commit y push
3. El workflow ejecuta el pipeline y actualiza `homicidios_clean.csv`

### Opción 2: Manual (Local)

```bash
# Colocar archivo Excel en data/raw/
python -m scripts.consolidar_y_limpiar

# Verificar integridad
python -m scripts.verificar_datos
python -m scripts.verificar_coordenadas

# Commit y push
git add homicidios_clean.csv data/processed/
git commit -m "Actualización de datos"
git push
```

---

## Pipeline ETL

### 1. Consolidación (`consolidar_y_limpiar.py`)

- Detecta automáticamente el archivo Excel 2025 más reciente
- Prioriza archivos con rango completo (ej: "enero-diciembre")
- Usa `smart_read_excel()` para encontrar la hoja de datos correcta
- Fusiona con el histórico 2014-2024

### 2. Limpieza (`limpiar_datos.py`)

- Normaliza nombres de columnas
- Procesa fechas y deriva `anio`, `mes`, `dia_semana`
- Corrige coordenadas (coma → punto decimal)
- Estandariza texto: mayúsculas, sin tildes
- Normaliza nombres de cantones (variantes conocidas)
- Categoriza rangos de edad

### 3. Validación

| Script | Propósito |
|--------|-----------|
| `verificar_datos.py` | Compara conteos Excel vs CSV |
| `verificar_coordenadas.py` | % de completitud geográfica por año |
| `verificar_cantones.py` | Detecta duplicados por ortografía |

---

## Notas Técnicas

### Formatos Excel del MDI

Los archivos del Ministerio del Interior suelen incluir:
- Hojas de presentación/metadatos antes de los datos
- Encabezados en filas variables (no siempre fila 0)

El script `smart_read_excel()` busca automáticamente la fila con "PROVINCIA" para ubicar los datos.

### Coordenadas

Ecuador usa formato con coma decimal en algunos exports. El pipeline convierte automáticamente a punto para compatibilidad con Leaflet.

### Codificación

Los CSV se generan en UTF-8 para evitar problemas con caracteres especiales.

---

## Transición Anual

### Al cerrar el año 2025

El archivo `mdi_homicidiosintencionalse_pm_2025_enero_diciembre.xlsx` ya contiene el año completo. Para iniciar 2026:

1. Fusionar 2025 con el histórico → crear `mdi_homicidios_intencionales_pm_2014_2025.xlsx`
2. Colocar en `data/raw/`
3. Actualizar referencia en `consolidar_y_limpiar.py` (línea del `archivo_historico`)

### Al recibir datos de 2026

Colocar el nuevo archivo con "2026" en el nombre en `data/raw/`. El script lo detectará automáticamente.

---

## Licencia

Datos públicos del Ministerio del Interior de Ecuador.
