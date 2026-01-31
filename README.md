# Observatorio de Seguridad - Ecuador

Dashboard interactivo para visualizar y analizar datos de homicidios intencionales en Ecuador (2014-2025).

**[Ver Dashboard en Vivo](https://jp1309.github.io/crimen/)**

---

## Descripcion General

Este proyecto proporciona una herramienta de visualizacion de datos de seguridad publica basada en informacion oficial del Ministerio del Interior de Ecuador. Permite explorar tendencias temporales, distribucion geografica y caracteristicas demograficas de los homicidios intencionales.

### Caracteristicas Principales

- **Visualizacion temporal**: Evolucion anual y mensual de casos
- **Analisis geografico**: Mapa de calor con geolocalizacion de incidentes
- **Estadisticas demograficas**: Piramide poblacional por edad y genero
- **Rankings territoriales**: Comparacion entre provincias y cantones
- **Filtros interactivos**: Por ano, mes, ubicacion, edad y sexo

---

## Estructura del Proyecto

```
crimen/
│
├── index.html                  # Pagina principal del dashboard
├── app.js                      # Logica frontend (graficos, filtros, mapa)
├── style.css                   # Estilos personalizados
├── homicidios_clean.csv        # Dataset limpio (produccion)
│
├── data/
│   ├── raw/                    # Archivos Excel originales del MDI
│   │   ├── mdi_homicidios_intencionales_pm_2014_2024.xlsx
│   │   └── mdi_homicidiosintencionalse_pm_2025_enero_diciembre.xlsx
│   │
│   └── processed/              # Archivos intermedios del pipeline
│       └── homicidios_consolidado.csv
│
├── scripts/                    # Pipeline ETL en Python
│   ├── __init__.py             # Documentacion del paquete
│   ├── consolidar_y_limpiar.py # Script principal del pipeline
│   ├── limpiar_datos.py        # Modulo de limpieza de datos
│   ├── verificar_datos.py      # Validacion de integridad
│   ├── verificar_coordenadas.py# Verificacion de geolocalizacion
│   └── verificar_cantones.py   # Deteccion de duplicados
│
└── .github/
    └── workflows/
        └── update_data.yml     # Automatizacion CI/CD
```

---

## Vistas del Dashboard

| Vista | Descripcion | Graficos |
|-------|-------------|----------|
| **Evolucion** | Tendencias temporales | Linea temporal, tipos de arma, distribucion horaria |
| **Ranking** | Analisis demografico y territorial | Piramide poblacional, ranking geografico |
| **Mapa** | Visualizacion geografica | Heatmap, marcadores individuales |

---

## Tecnologias Utilizadas

### Frontend
| Tecnologia | Proposito |
|------------|-----------|
| Vanilla JavaScript | Logica de aplicacion |
| [Chart.js](https://www.chartjs.org/) | Graficos interactivos |
| [Leaflet.js](https://leafletjs.com/) | Mapas y geolocalizacion |
| [Tailwind CSS](https://tailwindcss.com/) | Framework de estilos |
| [PapaParse](https://www.papaparse.com/) | Parsing de CSV |

### Backend (ETL)
| Tecnologia | Proposito |
|------------|-----------|
| Python 3.10+ | Lenguaje de procesamiento |
| [Pandas](https://pandas.pydata.org/) | Manipulacion de datos |
| [Openpyxl](https://openpyxl.readthedocs.io/) | Lectura de Excel |
| [Unidecode](https://pypi.org/project/Unidecode/) | Normalizacion de texto |

### Infraestructura
| Servicio | Proposito |
|----------|-----------|
| GitHub Pages | Hosting estatico |
| GitHub Actions | CI/CD automatizado |

---

## Guia de Uso

### Requisitos Previos

```bash
# Python 3.10 o superior
python --version

# Instalar dependencias
pip install pandas openpyxl unidecode numpy
```

### Actualizacion de Datos

#### Opcion 1: Automatica (Recomendada)

1. Colocar el nuevo archivo Excel en `data/raw/`
2. Hacer commit y push
3. GitHub Actions ejecuta el pipeline automaticamente
4. El dashboard se actualiza en ~2 minutos

#### Opcion 2: Manual (Local)

```bash
# 1. Colocar archivo Excel en data/raw/

# 2. Ejecutar pipeline
python -m scripts.consolidar_y_limpiar

# 3. Verificar resultados
python -m scripts.verificar_datos
python -m scripts.verificar_coordenadas

# 4. Subir cambios
git add homicidios_clean.csv data/processed/
git commit -m "Actualizacion de datos"
git push
```

---

## Pipeline ETL

El pipeline procesa los datos en tres etapas:

### Etapa 1: Consolidacion

**Script:** `scripts/consolidar_y_limpiar.py`

```
Excel Historico (2014-2024) ─┐
                             ├──> CSV Consolidado ──> Limpieza
Excel Actual (2025)         ─┘
```

**Funcionalidades:**
- Detecta automaticamente el archivo Excel 2025 mas reciente
- Prioriza archivos con rango completo (ej: "enero-diciembre" = prioridad 13)
- Usa `smart_read_excel()` para encontrar la hoja de datos correcta
- Los archivos del MDI suelen tener hojas de presentacion que se ignoran

### Etapa 2: Limpieza

**Script:** `scripts/limpiar_datos.py`

| Proceso | Descripcion |
|---------|-------------|
| Columnas | Normaliza a minusculas con guiones bajos |
| Fechas | Extrae `anio`, `mes`, `dia_semana` |
| Coordenadas | Convierte coma a punto decimal |
| Texto | Mayusculas, sin tildes (unidecode) |
| Cantones | Normaliza variantes conocidas |
| Edad | Categoriza en rangos (Nino, Joven, Adulto, etc.) |

### Etapa 3: Validacion

| Script | Proposito | Comando |
|--------|-----------|---------|
| `verificar_datos.py` | Compara conteos Excel vs CSV | `python -m scripts.verificar_datos` |
| `verificar_coordenadas.py` | % completitud geografica por ano | `python -m scripts.verificar_coordenadas` |
| `verificar_cantones.py` | Detecta duplicados ortograficos | `python -m scripts.verificar_cantones` |

---

## Esquema de Datos

### Columnas Principales del CSV

| Columna | Tipo | Descripcion |
|---------|------|-------------|
| `fecha_infraccion` | datetime | Fecha del incidente |
| `anio` | int | Ano (2014-2025) |
| `mes` | int | Mes (1-12) |
| `dia_semana` | string | Lunes, Martes, etc. |
| `provincia` | string | Provincia de Ecuador |
| `canton` | string | Canton |
| `coordenada_x` | float | Longitud (para Leaflet) |
| `coordenada_y` | float | Latitud (para Leaflet) |
| `sexo` | string | HOMBRE, MUJER, DESCONOCIDO |
| `edad` | float | Edad de la victima |
| `rango_edad` | string | Nino, Adolescente, Joven, Adulto, Adulto Mayor, Anciano |
| `arma` | string | Tipo de arma utilizada |
| `tipo_muerte` | string | HOMICIDIO, ASESINATO, etc. |

---

## Notas Tecnicas

### Formatos Excel del MDI

Los archivos del Ministerio del Interior tienen caracteristicas especiales:

1. **Hojas de presentacion**: La primera hoja suele ser metadata
2. **Encabezados variables**: Los datos no siempre empiezan en la fila 0
3. **Formato de coordenadas**: Usan coma como separador decimal

El script `smart_read_excel()` maneja estos casos automaticamente buscando la fila que contiene "PROVINCIA".

### Compatibilidad de Locale

El script de limpieza no depende del locale del sistema operativo. Los dias de la semana se mapean manualmente de ingles a espanol para garantizar compatibilidad en GitHub Actions (Ubuntu).

### Coordenadas Geograficas

- Ecuador: Latitud ~-1.8, Longitud ~-78
- Los datos recientes (2023-2025) tienen ~100% de completitud
- Los anos anteriores tienen completitud variable (ver `verificar_coordenadas.py`)

---

## Transicion Anual

### Al cerrar un ano (ej: 2025 -> 2026)

1. **Fusionar historico**: Combinar 2014-2024 + 2025 en un nuevo archivo
   ```
   mdi_homicidios_intencionales_pm_2014_2025.xlsx
   ```

2. **Actualizar script**: Cambiar `archivo_historico` en `consolidar_y_limpiar.py`

3. **Nuevo ano**: Colocar archivo 2026 en `data/raw/` - se detecta automaticamente

### Nomenclatura de Archivos

El script detecta el archivo mas reciente basandose en:

| Patron | Prioridad |
|--------|-----------|
| `*enero*diciembre*` | 13 (ano completo) |
| `*diciembre*` | 12 |
| `*noviembre*` | 11 |
| `*_11_*` | 11 |
| ... | ... |

---

## Estadisticas Actuales

| Metrica | Valor |
|---------|-------|
| Periodo | 2014-2025 |
| Total registros | ~39,754 |
| Ultimo mes | Diciembre 2025 |
| Completitud geografica | ~76.5% |

---

## Fuente de Datos

**Ministerio del Interior de Ecuador**
- Direccion de Estadistica y Economia de la Seguridad
- Datos de la Policia Nacional del Ecuador

---

## Licencia

Los datos son de dominio publico, proporcionados por el Ministerio del Interior de Ecuador.

El codigo fuente de este proyecto esta disponible bajo licencia MIT.
