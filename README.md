# Observatorio de Seguridad — Ecuador

Dashboard interactivo para visualizar y analizar homicidios intencionales en Ecuador desde 2014.

**[Ver dashboard en vivo](https://jp1309.github.io/crimen/)**

## Qué ofrece

- Evolución anual y mensual de casos.
- Distribución por arma, hora, edad y sexo.
- Rankings provinciales y cantonales.
- Mapa de calor y marcadores georreferenciados.
- Filtros temporales, territoriales y demográficos.

Los datos provienen del conjunto oficial [Homicidios Intencionales — Datos Abiertos Ecuador](https://www.datosabiertos.gob.ec/dataset/homicidios-intencionales), publicado por el Ministerio del Interior.

## Arquitectura de datos

```text
API de Datos Abiertos Ecuador (CKAN)
               │
               ▼
     scripts/descargar_datos.py
               │
       ┌───────┴────────┐
       ▼                ▼
 histórico.xlsx     actual.xlsx
       └───────┬────────┘
               ▼
 scripts/consolidar_y_limpiar.py
               │
       ┌───────┴──────────────┐
       ▼                      ▼
data/processed/          homicidios_clean.csv
homicidios_consolidado.csv     │
                              ▼
                         Dashboard web
```

Las fuentes locales tienen nombres canónicos y estables:

- `data/raw/mdi_homicidios_intencionales_pm_historico.xlsx`
- `data/raw/mdi_homicidios_intencionales_pm_actual.xlsx`
- `data/source_manifest.json`: URL, identificador, fecha oficial, tamaño y SHA-256 de cada fuente.

### Por qué el año actual se reemplaza completo

El archivo mensual del Ministerio es acumulativo. Una publicación nueva no contiene únicamente el último mes: también puede corregir registros de todos los meses anteriores del mismo año. Por eso el pipeline reemplaza el Excel anual completo y reconstruye todo el CSV. Nunca concatena el nuevo archivo con una versión anterior del mismo año.

El pipeline también detiene la ejecución si el histórico y el archivo actual contienen años solapados, evitando duplicados durante una transición anual.

## Actualización automática

El workflow [`.github/workflows/update_data.yml`](.github/workflows/update_data.yml) realiza la primera consulta el día 15 de cada mes y vuelve a consultar aproximadamente cada tres días. Las revisiones de los días 2, 5, 8 y 11 permiten continuar si la publicación se retrasa hasta el mes siguiente.

Cada intento:

1. Consulta la [API oficial del conjunto](https://www.datosabiertos.gob.ec/api/3/action/package_show?id=homicidios-intencionales).
2. Descarga y valida las fuentes histórica y anual.
3. Compara sus SHA-256 con las copias locales.
4. Si no cambiaron, termina sin crear un commit.
5. Si cambiaron, reemplaza las fuentes de forma atómica y reconstruye todos los datos.
6. Exige igualdad exacta entre los conteos por año de los Excel y del CSV final.
7. Guarda un único commit y solicita la publicación de GitHub Pages.

El workflow también puede ejecutarse manualmente desde la pestaña **Actions**.

## Ejecución local

Requisitos: Python 3.10 o superior.

```bash
python -m pip install --requirement requirements.txt

# Consultar, descargar y validar fuentes oficiales
python -m scripts.descargar_datos

# Consolidar y limpiar
python -m scripts.consolidar_y_limpiar

# QA obligatorio
python -m scripts.verificar_datos
python -m scripts.verificar_coordenadas

# Pruebas del sincronizador
python -m unittest discover -v
```

Para comprobar la fuente sin reemplazar archivos locales:

```bash
python -m scripts.descargar_datos --dry-run
```

## Estructura del proyecto

```text
crimen/
├── index.html
├── app.js
├── style.css
├── homicidios_clean.csv
├── requirements.txt
├── data/
│   ├── source_manifest.json
│   ├── raw/
│   │   ├── mdi_homicidios_intencionales_pm_historico.xlsx
│   │   └── mdi_homicidios_intencionales_pm_actual.xlsx
│   └── processed/
│       └── homicidios_consolidado.csv
├── scripts/
│   ├── configuracion.py
│   ├── descargar_datos.py
│   ├── consolidar_y_limpiar.py
│   ├── limpiar_datos.py
│   ├── verificar_datos.py
│   ├── verificar_coordenadas.py
│   └── verificar_cantones.py
├── tests/
│   └── test_descargar_datos.py
└── .github/workflows/update_data.yml
```

## Validaciones

- Los dos recursos primarios deben estar activos y ser XLSX.
- Cada archivo debe superar 50 KB, ser un ZIP/XLSX válido y contener una tabla con `PROVINCIA`.
- La fuente histórica y la anual no pueden compartir años.
- El número total de filas y el desglose anual deben coincidir exactamente entre Excel y CSV.
- Las escrituras de fuentes, manifiesto y CSV se realizan de forma atómica.

## Estado actual

| Métrica | Valor |
|---|---:|
| Período | enero de 2014 – junio de 2026 |
| Registros | 43.975 |
| Registros de 2026 | 4.154 |
| Completitud geográfica total | 96,4 % |

## Tecnologías

- Frontend: JavaScript, Chart.js, Leaflet, Tailwind CSS y PapaParse.
- Datos: Python, pandas, openpyxl y Unidecode.
- Automatización: GitHub Actions y GitHub Pages.

## Licencia y fuente

Los datos son públicos y se distribuyen bajo Creative Commons Attribution según el catálogo oficial. El código del proyecto está disponible bajo licencia MIT.
