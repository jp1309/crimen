# Guía de contribución

## Actualizar los datos

La vía recomendada es ejecutar manualmente el proceso de la automatización local; GitHub Actions reconstruye y repite los controles después del `push`:

```bash
python -m pip install --requirement requirements.txt
python -m scripts.descargar_datos
python -m scripts.consolidar_y_limpiar
python -m scripts.verificar_datos
python -m scripts.verificar_coordenadas
python -m unittest discover -v
```

La fuente oficial es el conjunto [Homicidios Intencionales — Datos Abiertos Ecuador](https://www.datosabiertos.gob.ec/dataset/homicidios-intencionales). El sincronizador consulta su API, por lo que no se deben copiar ni renombrar manualmente los archivos publicados.

### Regla fundamental

El Excel del año actual es acumulativo y puede revisar meses anteriores. Siempre debe reemplazarse completo. No se debe anexar únicamente el mes nuevo ni conservar dos archivos anuales activos en `data/raw/`.

### Revisar los cambios

```bash
git status --short
git diff --stat
```

Los archivos esperados tras una actualización son:

- `data/raw/mdi_homicidios_intencionales_pm_historico.xlsx`, si la fuente histórica cambió.
- `data/raw/mdi_homicidios_intencionales_pm_actual.xlsx`, si cambió el acumulado anual.
- `data/source_manifest.json`.
- `data/processed/homicidios_consolidado.csv`.
- `homicidios_clean.csv`.

No se debe hacer commit si `scripts.verificar_datos` falla.

`scripts.verificar_coordenadas` informa la cobertura espacial, pero no aplica actualmente un umbral de rechazo. Una caída inesperada debe investigarse y documentarse antes de publicar.

## Probar sin modificar datos

```bash
python -m scripts.descargar_datos --dry-run
```

Esto descarga y valida temporalmente las fuentes, pero no reemplaza los Excel ni el manifiesto.

## Agregar normalizaciones

Si aparecen variantes ortográficas de cantones:

1. Ejecutar `python -m scripts.verificar_cantones`.
2. Agregar el mapeo a `canton_mapping` en `scripts/limpiar_datos.py`.
3. Reconstruir, ejecutar todo el QA y revisar los cambios.

## Cuando cambie el formato oficial

El sincronizador y el ETL buscan automáticamente una hoja cuya cabecera contenga `PROVINCIA` y al menos uno de estos campos: `FECHA`, `ZONA` o `CANTON`.

Si una publicación no pasa la validación:

1. No reemplazar manualmente los archivos canónicos.
2. Revisar la hoja y fila de encabezado del nuevo Excel.
3. Ajustar la detección en `scripts/descargar_datos.py` y `smart_read_excel()`.
4. Agregar una prueba que reproduzca el nuevo formato.

## Mantener la documentación

Todo cambio de comportamiento debe actualizar la documentación correspondiente en el mismo commit:

- Cambios de horario, tarea o publicación: `docs/AUTOMATIZACION.md` y `docs/OPERACION_Y_RECUPERACION.md`.
- Cambios de columnas, tipos o normalizaciones: `docs/DICCIONARIO_DATOS.md`.
- Cambios de vistas, filtros, dependencias o carga del CSV: `docs/ARQUITECTURA_FRONTEND.md`.
- Cambios de estructura o comandos principales: `README.md` y `docs/README.md`.

No agregue cifras mensuales estáticas al README: quedan obsoletas en la siguiente publicación. El estado vigente debe obtenerse mediante los controles o `data/source_manifest.json`.

## Revisión mínima antes de un pull request

```bash
python -m unittest discover -v
python -m scripts.verificar_datos
python -m scripts.verificar_coordenadas
git diff --check
```

Además, compruebe todos los enlaces Markdown locales y revise manualmente el dashboard si cambió `index.html`, `style.css`, `app.js` o el esquema del CSV.
