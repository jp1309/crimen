# Guía de contribución

## Actualizar los datos

La vía recomendada es ejecutar manualmente el mismo proceso que usa GitHub Actions:

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
