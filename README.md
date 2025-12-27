# Observatorio de Seguridad - Ecuador 🇪🇨

Dashboard interactivo para el análisis visual de datos de homicidios intencionales en Ecuador (2014-2025).

🔗 **[Ver Dashboard En Vivo](https://jp1309.github.io/crimen/)**

---

## 🤖 Documentación Técnica (Agent Context)

Esta sección describe la arquitectura del proyecto para facilitar el mantenimiento por parte de agentes de IA o desarrolladores.

### 📂 Estructura del Proyecto

*   **Frontend (SPA):**
    *   `index.html`: Punto de entrada. Carga librerías (Leaflet, Chart.js, Tailwind).
    *   `app.js`: Lógica principal. Consume `homicidios_clean.csv`. Maneja estado global `rawData`, filtros y renderizado de gráficos.
    *   `style.css`: Estilos custom (complementando Tailwind).
*   **Data Pipeline (Python):**
    *   `consolidar_y_limpiar.py`: **Script Principal**.
        *   Detecta automáticamente archivo Excel 2025 (nombres flexibles).
        *   Usa `smart_read_excel` para buscar la hoja de datos correcta (ignorando portadas/metadata).
        *   Fusiona con histórico `mdi_homicidios_intencionales_pm_2014_2024.xlsx`.
        *   Invoca `inspect_excel.py`.
    *   `inspect_excel.py`: Módulo de limpieza ETL.
        *   Normaliza columnas, fechas, coordenadas (coma a punto) y texto (elimina tildes con `unidecode`).
        *   Estandariza nombres de cantones (ej. correcciones en Guayas y Manabí).
        *   Genera `homicidios_clean.csv`.
*   **QA & Validación:**
    *   `verify_data.py`: Compara conteo de filas (Excel vs CSV Output).
    *   `check_coords.py`: Calcula % de completitud de lat/long por año.
    *   `inspect_cantons.py`: Busca duplicados fonéticos en nombres de cantones.

### 🔄 Flujo de Actualización de Datos

1.  **Input:** Subir nuevo archivo Excel (ej: `2025_11_homicidios.xlsx`) a la raíz.
2.  **Proceso:** Ejecutar `python consolidar_y_limpiar.py`.
    *   El script detectará el archivo nuevo, buscará la hoja con columna "PROVINCIA", y regenerará el CSV.
3.  **Output:** `homicidios_clean.csv` se actualiza.
4.  **Deploy:** Commit & Push. GitHub Pages sirve el nuevo CSV estático.

### ⚠️ Puntos Críticos

*   **Formatos Excel:** Los archivos del Ministerio del Interior suelen tener hojas de presentación o metadatos en la primera pestaña. Siempre usar la lógica de búsqueda de encabezado "Provincia" implementada en `smart_read_excel`.
*   **Coordenadas:** Los decimales a veces vienen con coma (`,`). El script de limpieza debe forzar conversión a punto (`.`) para que Leaflet/Mapbox funcionen adecuadamente.
*   **Codificación:** Los CSV generados deben ser UTF-8 estándar para evitar problemas con tildes en el frontend.

---

## 📊 Vistas del Dashboard

1.  **Evolución:** Timeline anual/mensual, Tipos de Arma, Hora del delito.
2.  **Ranking:** Demografía (Pirámide Poblacional) y Ranking Geográfico (Provincia/Cantón).
3.  **Mapa:** Geolocalización de puntos (Heatmap + Clustered Markers).

## 🛠️ Tecnologías

*   **Frontend:** Vanilla JS, Chart.js, Leaflet, Tailwind CSS.
*   **Backend (ETL):** Python (Pandas, Numpy, Unidecode, Openpyxl).
*   **Infraestructura:** GitHub Actions & GitHub Pages.

---

## 🔮 Guía de Mantenimiento Futuro

### Caso 1: Cierre del Año 2025 (Enero 2026)
Cuando tengas el archivo final con todos los datos de 2025 (ej. `Homicidios_2025_Completo.xlsx`):

1.  **Limpiar:** Elimina o mueve a una carpeta de respaldo el archivo parcial anterior (ej. `2025_11_...xlsx`).
2.  **Cargar:** Pon el nuevo archivo completo en la raíz. Asegúrate de que el nombre tenga "2025".
3.  **Ejecutar:** Correr `python consolidar_y_limpiar.py`. El script detectará el único archivo 2025 presente y reconstruirá el CSV.
4.  **Verificar:** Correr `python verify_data.py` (debería haber ~0 diferencias).

### Caso 2: Transición al Año 2026
Cuando empieces a recibir datos de 2026:

*   **Opción Recomendada:** Fusionar manualmente el archivo 2025 completo con el histórico `2014-2024` para crear un nuevo archivo maestro `mdi_homicidios_intencionales_pm_2014_2025.xlsx`.
*   **Ajuste de Script:** Si decides mantener 3 archivos separados (Histórico + 2025 + 2026), se deberá editar `consolidar_y_limpiar.py` para que lea y concatene tres fuentes en lugar de dos.
