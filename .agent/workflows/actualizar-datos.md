---
description: Pipeline para actualizar, consolidar y subir nuevos datos de homicidios al dashboard
---

Este workflow automatiza la unión de los archivos Excel originales, la limpieza de datos y la publicación en GitHub.

### 📋 Requisitos Previos
1. El nuevo archivo Excel (ej: `...enero_noviembre.xlsx`) debe estar en la carpeta raíz.
2. Los scripts `inspect_excel.py` y `consolidar_y_limpiar.py` deben existir.

### 🚀 Pasos de Ejecución

// turbo
1. **Consolidar y Limpiar Datos**
   Ejecuta el script para unir el histórico con el nuevo mes y generar el CSV final.
   ```powershell
   python consolidar_y_limpiar.py
   ```

2. **Verificar Integridad**
   Asegúrate de que los conteos de filas coincidan.
   ```powershell
   python verify_data.py
   ```

// turbo
3. **Preparar archivos para Git**
   Agrega los nuevos archivos de datos y los actualizados al staging.
   ```powershell
   git add *.xlsx homicidios_clean.csv homicidios_consolidado.csv verify_data.py README.md
   ```

4. **Hacer Commit y Subir**
   Envía los cambios a GitHub para que GitHub Pages se actualice automáticamente.
   ```powershell
   git commit -m "Actualización mensual de datos: Noviembre 2025"
   git push origin main
   ```

---
**Nota:** Una vez que el `git push` termine, GitHub Pages tardará aproximadamente 1-2 minutos en reflejar los cambios en la URL pública.
