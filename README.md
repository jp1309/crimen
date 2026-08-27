# Observatorio de Seguridad — Ecuador

Dashboard interactivo para visualizar y analizar homicidios intencionales en Ecuador desde 2014.

**[Ver dashboard en vivo](https://jp1309.github.io/crimen/)**

[![Actualizar datos y dashboard](https://github.com/jp1309/crimen/actions/workflows/update_data.yml/badge.svg)](https://github.com/jp1309/crimen/actions/workflows/update_data.yml)

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

## Documentación

- [Índice de documentación](docs/README.md)
- [Automatización mensual](docs/AUTOMATIZACION.md): horario y operación íntegramente remota en GitHub Actions.
- [Operación y recuperación](docs/OPERACION_Y_RECUPERACION.md): actualización manual, fallos, transición anual y reversión.
- [Diccionario de datos](docs/DICCIONARIO_DATOS.md): granularidad, 37 columnas, valores faltantes y campos derivados.
- [Arquitectura del frontend](docs/ARQUITECTURA_FRONTEND.md): carga, filtros, vistas, mapa, dependencias y publicación.
- [Guía de contribución](CONTRIBUTING.md): reglas para modificar datos y código.

## Actualización automática

La descarga se ejecuta íntegramente en [GitHub Actions](.github/workflows/update_data.yml), sin depender de Codex ni de una computadora encendida. Consulta a las 09:17, `America/New_York`, los días 15, 18, 21, 24, 27 y 30. Las revisiones de los días 2, 5, 8 y 11 cubren publicaciones retrasadas hasta el mes siguiente.

El portal oficial bloquea las direcciones de centros de datos, incluidos los runners de GitHub y relays serverless convencionales. El workflow prueba primero la ruta directa y, ante un bloqueo, usa el secreto `SOURCE_HTTPS_PROXY`, que debe contener la URL de un proxy HTTPS administrado con salida ISP/residencial. Una vez configurado ese secreto, todo el ciclo ocurre dentro del runner remoto y no depende de Codex ni de una computadora encendida.

Cada intento remoto:

1. Consulta la [API oficial del conjunto](https://www.datosabiertos.gob.ec/api/3/action/package_show?id=homicidios-intencionales). Si el catálogo bloquea la API desde GitHub Actions, usa las URLs oficiales estables de ambos recursos.
2. Descarga y valida las fuentes histórica y anual.
3. Compara sus SHA-256 con las copias locales.
4. Si no cambiaron, termina sin crear un commit.
5. Si cambiaron, reemplaza las fuentes de forma atómica y reconstruye todos los datos.
6. Exige igualdad exacta entre los conteos por año de los Excel y del CSV final.
7. Guarda un único commit y hace `push` a `main`.
8. Solicita la publicación de GitHub Pages y comprueba el SHA-256 del CSV público.

Cuando una ejecución falla, el workflow crea o actualiza un único issue operativo. La siguiente ejecución correcta cierra el incidente automáticamente. La comparación con Pages admite únicamente la conversión CRLF→LF que realiza la publicación estática; cualquier diferencia de contenido sigue siendo un error.

El mismo workflow puede ejecutarse inmediatamente desde la pestaña **Actions** mediante `Run workflow`.

## Ejecución local

Requisitos: Python 3.10 o superior.

```bash
python -m pip install --requirement requirements.txt

# Consultar, descargar y validar fuentes oficiales
python -m scripts.descargar_datos

# Consolidar y limpiar
python -m scripts.consolidar_y_limpiar

# Integridad obligatoria y diagnóstico geográfico
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
├── LICENSE
├── CONTRIBUTING.md
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
├── docs/
│   ├── README.md
│   ├── AUTOMATIZACION.md
│   ├── OPERACION_Y_RECUPERACION.md
│   ├── DICCIONARIO_DATOS.md
│   └── ARQUITECTURA_FRONTEND.md
└── .github/workflows/update_data.yml
```

## Validaciones

- Los dos recursos primarios deben estar activos y ser XLSX.
- Los identificadores estables de los recursos permiten descargar nuevas versiones aunque cambie el nombre mensual del Excel.
- Cada archivo debe superar 50 KB, ser un ZIP/XLSX válido y contener una tabla con `PROVINCIA`.
- La fuente histórica y la anual no pueden compartir años.
- El número total de filas y el desglose anual deben coincidir exactamente entre Excel y CSV.
- Las escrituras de fuentes, manifiesto y CSV se realizan de forma atómica.
- La cobertura de coordenadas se reporta por año como diagnóstico; no se inventan ubicaciones ni se ocultan periodos con cobertura baja.

## Comprobar el estado vigente

Las cifras cambian mensualmente y no se duplican como una tabla manual en este README. Para obtener el total y el desglose anual de la versión actual:

```bash
python -m scripts.verificar_datos
python -m scripts.verificar_coordenadas
```

`data/source_manifest.json` identifica la fecha, el nombre oficial, el tamaño y el SHA-256 de las fuentes exactas. El dashboard público muestra el periodo disponible después de cada publicación.

## Tecnologías

- Frontend: JavaScript, Chart.js, Leaflet, Tailwind CSS y PapaParse.
- Datos: Python, pandas, openpyxl y Unidecode.
- Automatización: GitHub Actions y GitHub Pages.

## Licencia y fuente

Los datos son públicos y se distribuyen bajo Creative Commons Attribution según el catálogo oficial. El código del proyecto está disponible bajo la [licencia MIT](LICENSE).
