# Observatorio de Seguridad - Ecuador 🇪🇨

Dashboard interactivo para el análisis visual de datos de homicidios intencionales en Ecuador (2014-2025). Proyecto enfocado en democratizar el acceso a estadísticas de seguridad mediante visualizaciones modernas y dinámicas.

🔗 **[Ver Dashboard En Vivo](https://jp1309.github.io/crimen/)**

---

## 📊 Vistas Principales

*   **Evolución Histórica:** Tendencias temporales, métodos utilizados (armas) y distribución por franque horaria.
*   **Ranking y Demografía:** Análisis por provincia/cantón y pirámide de víctimas por edad y sexo.
*   **Geolocalización:** Mapa de calor con precisión de coordenadas (datos 2023-2025).

## ⚡ Automatización de Datos

El repositorio cuenta con un pipeline automático (**GitHub Actions**). El proceso de actualización es simple:
1.  Subir el nuevo archivo Excel oficial del Ministerio del Interior a la raíz del repositorio.
2.  El sistema detectará el archivo, unirá los datos históricos y regenerará el archivo de visualización (`homicidios_clean.csv`) de forma automática.

## 🛠️ Tecnologías

*   **Frontend:** Vanilla JS, Chart.js, Leaflet, Tailwind CSS.
*   **Procesamiento:** Python (Pandas, Numpy, Unidecode).
*   **Infraestructura:** GitHub Actions & GitHub Pages.

---
> **Nota Técnica:** Los datos son procesados a partir de fuentes oficiales del Ministerio del Interior del Ecuador. El archivo consolidado final incluye más de 38,000 registros validados.
