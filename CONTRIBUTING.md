# Guia de Contribucion

## Actualizacion de Datos

### Paso 1: Obtener el archivo Excel

Descargar el archivo mas reciente del Ministerio del Interior de Ecuador. El formato tipico es:

```
mdi_homicidiosintencionalse_pm_2025_[mes].xlsx
```

### Paso 2: Colocar en la carpeta correcta

```bash
# Mover el archivo a data/raw/
mv archivo_descargado.xlsx data/raw/
```

### Paso 3: Ejecutar el pipeline

```bash
# Ejecutar consolidacion y limpieza
python -m scripts.consolidar_y_limpiar

# Verificar integridad
python -m scripts.verificar_datos

# Verificar coordenadas (opcional)
python -m scripts.verificar_coordenadas
```

### Paso 4: Revisar y subir

```bash
# Verificar cambios
git status
git diff homicidios_clean.csv | head -50

# Subir cambios
git add homicidios_clean.csv data/
git commit -m "Datos actualizados: [mes] 2025"
git push
```

---

## Agregar Nuevas Normalizaciones

Si detectas variantes de nombres de cantones:

1. Ejecutar verificacion:
   ```bash
   python -m scripts.verificar_cantones
   ```

2. Agregar mapeo en `scripts/limpiar_datos.py`:
   ```python
   canton_mapping = {
       'NOMBRE_VIEJO': 'NOMBRE_CORRECTO',
       # ... agregar nuevos
   }
   ```

3. Re-ejecutar pipeline y verificar.

---

## Estructura de Archivos Excel

Los archivos del MDI tienen estructura variable. Si un archivo nuevo no se procesa correctamente:

1. Abrir el Excel y verificar:
   - Cual hoja contiene los datos
   - En que fila estan los encabezados
   - Si existe la columna "PROVINCIA"

2. Si es necesario, ajustar `smart_read_excel()` en `consolidar_y_limpiar.py`.

---

## Reportar Problemas

Abrir un issue en GitHub con:

1. Descripcion del problema
2. Archivo Excel que causa el error (si aplica)
3. Mensaje de error completo
4. Sistema operativo y version de Python
