# Arquitectura del frontend

## Resumen

El dashboard es un sitio estático. No usa servidor de aplicaciones, base de datos en línea ni paso de compilación. GitHub Pages sirve `index.html`, `style.css`, `app.js` y `homicidios_clean.csv`; todo el filtrado y la agregación se ejecutan en el navegador.

```text
GitHub Pages
  ├─ index.html ───── estructura, filtros y contenedores
  ├─ style.css ────── estilos propios
  ├─ app.js ───────── carga, estado, filtros y visualizaciones
  └─ homicidios_clean.csv
          │
          ▼
     Papa Parse
          │
          ▼
  rawData en memoria
          │
          ├─ filtros de periodo y territorio
          ├─ filtros demográficos
          └─ conjunto filtrado
                 │
                 ├─ Chart.js
                 └─ Leaflet + Leaflet.heat
```

## Archivos y responsabilidades

| Archivo | Responsabilidad |
|---|---|
| `index.html` | Estructura, navegación, controles, lienzos de gráficos, mapa y carga de dependencias CDN |
| `style.css` | Estilos que complementan Tailwind y personalizan gráficos, filtros y mapa |
| `app.js` | Estado global, carga del CSV, filtros, agregaciones, gráficos, mapa y utilidades |
| `homicidios_clean.csv` | Contrato de datos público consumido por el navegador |

## Inicialización

1. `DOMContentLoaded` llama a `initDashboard()`.
2. Papa Parse descarga `homicidios_clean.csv` con encabezados y tipado dinámico.
3. El resultado completo se guarda en `rawData`.
4. `populateFilters()` deriva años, provincias y cantones disponibles.
5. `updateDashboard()` filtra y renderiza únicamente la vista activa.

Una falla de carga se muestra como alerta y deja el detalle técnico en la consola del navegador.

## Estado del navegador

| Variable | Función |
|---|---|
| `rawData` | Filas completas del CSV cargadas en memoria |
| `chartInstances` | Instancias activas de Chart.js para destruirlas antes de redibujar |
| `mapInstance` | Mapa Leaflet reutilizado entre filtros |
| `heatLayer` | Capa de calor activa |
| `currentView` | Vista activa: `timeline`, `ranking` o `map` |
| `geoRankMode` | Nivel del ranking territorial: provincia o cantón |

El estado no se persiste en URL ni almacenamiento local; recargar la página restablece los filtros.

## Filtros

`getFilteredData()` aplica, en este orden lógico:

- Periodo inclusivo entre año/mes inicial y final.
- Una o varias provincias.
- Uno o varios cantones disponibles para las provincias elegidas.
- Uno o varios rangos de edad.
- Uno o varios valores de sexo.

El valor `all` desactiva el filtro correspondiente. Si `rango_edad` o `sexo` están vacíos, el frontend los trata como `DESCONOCIDO`.

El periodo predeterminado comienza en enero del año anterior y termina en el último mes disponible del año más reciente. Al entrar al mapa, el periodo cambia al año más reciente para reducir el volumen de puntos.

## Vistas y funciones de renderizado

| Vista | Funciones | Resultado |
|---|---|---|
| Evolución | `renderTimeline`, `renderWeaponStats`, `renderHourDistribution` | Serie temporal, distribución por arma y distribución horaria |
| Rankings | `renderDemographics`, `renderGeoRanking` | Pirámide/demografía y ranking provincial o cantonal |
| Mapa | `renderMap` | Mapa base, calor, marcadores y detalles emergentes |

`updateDashboard()` actualiza el total filtrado y solo ejecuta las funciones de la vista visible. Los gráficos anteriores se destruyen mediante `destroyChart()` para evitar instancias duplicadas.

## Mapa

- Biblioteca: Leaflet.
- Cartografía base: CARTO Voyager con atribución a OpenStreetMap y CARTO.
- Densidad: `leaflet-heat`.
- Detalle: un marcador circular por registro con coordenadas utilizables.
- Los registros con coordenadas vacías o `0, 0` no aparecen en el mapa.
- Cuando el conjunto filtrado tiene menos de 5.000 filas, el mapa ajusta automáticamente sus límites.

La cobertura espacial no es homogénea en todos los años. Antes de comparar mapas históricos, ejecute `python -m scripts.verificar_coordenadas`.

## Dependencias externas

El HTML carga desde CDN:

| Dependencia | Uso | Estado de versión |
|---|---|---|
| Tailwind CSS | Utilidades visuales | Script CDN sin compilación local |
| Papa Parse 5.4.1 | Lectura del CSV | Fijada |
| Chart.js | Gráficos | No fijada en la URL actual |
| chartjs-plugin-datalabels 2.0.0 | Etiquetas | Fijada |
| Leaflet 1.9.4 | Mapa | Fijada |
| Leaflet.heat | Capa de calor | No fijada en la URL actual |
| CARTO/OSM | Teselas del mapa | Servicio externo |
| Google Fonts | Tipografía | Servicio externo |

No hay instalación JavaScript local ni archivo de bloqueo. Un cambio incompatible o una indisponibilidad de CDN puede afectar el dashboard aunque los archivos del repositorio no cambien. Al modificar dependencias, se recomienda fijar versiones y comprobar consola, gráficos y mapa antes de publicar.

## Contrato con los datos

El frontend depende directamente de estas columnas:

```text
anio, mes, provincia, canton, rango_edad, sexo,
fecha_infraccion, hora_infraccion, arma, edad,
coordenada_x, coordenada_y
```

Otras columnas pueden alimentar etiquetas y análisis futuros. Cualquier cambio de nombre o tipo debe actualizar simultáneamente `app.js`, el ETL, las pruebas y [DICCIONARIO_DATOS.md](DICCIONARIO_DATOS.md).

## Desarrollo local

El CSV se descarga por HTTP; abrir `index.html` directamente como archivo puede activar restricciones del navegador. Use un servidor estático desde la raíz:

```bash
python -m http.server 8000
```

Abra `http://localhost:8000/` y compruebe:

1. La consola no muestra errores.
2. El total cambia al aplicar filtros.
3. Las tres vistas se renderizan.
4. Provincia y cantón se encadenan correctamente.
5. El mapa muestra calor y marcadores para el periodo reciente.
6. La página funciona en ancho móvil y de escritorio.

## Agregar una visualización

1. Añadir el contenedor accesible en `index.html`.
2. Crear una función `render...` en `app.js` que reciba el conjunto ya filtrado.
3. Registrar y destruir la instancia de Chart.js en `chartInstances`, si aplica.
4. Llamarla únicamente desde la vista correspondiente en `updateDashboard()`.
5. Documentar las columnas utilizadas y su interpretación.
6. Probar valores vacíos, selección `all`, periodos pequeños y ausencia de coordenadas.

## Publicación

La rama `main` es la fuente de GitHub Pages. Un cambio del frontend puede publicarse mediante un commit normal; un cambio de datos debe seguir obligatoriamente [OPERACION_Y_RECUPERACION.md](OPERACION_Y_RECUPERACION.md).
