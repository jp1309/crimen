# Dashboard de Homicidios - Ecuador

## 📊 Descripción del Proyecto

Este es un **dashboard interactivo** que visualiza datos de homicidios intencionales en Ecuador desde 2014 hasta 2025. El proyecto procesa y presenta datos oficiales del MDI (Ministerio del Interior) de manera visual y accesible para análisis de seguridad ciudadana.

## 🎯 Objetivo

Crear una herramienta web interactiva y publicable (vía GitHub Pages) que permita:
- Analizar tendencias históricas de homicidios
- Identificar patrones geográficos y temporales
- Visualizar perfiles demográficos de víctimas
- Explorar datos a través de filtros dinámicos

---

## 📁 Estructura del Proyecto

```
crimen/
├── index.html                          # Interfaz principal del dashboard
├── app.js                              # Lógica de visualización y filtros
├── style.css                           # Estilos personalizados
├── homicidios_clean.csv               # Datos procesados (13MB+)
├── homicidios_consolidado.csv         # Datos consolidados
├── README.md                          # Este archivo
│
├── Archivos Python (procesamiento):
│   ├── inspect_excel.py               # Inspección de archivos Excel originales
│   ├── inspect_cantons.py             # Validación de cantones
│   ├── check_coords.py                # Verificación de coordenadas
│   └── verify_data.py                 # Validación de datos
│
└── Datos originales (Excel):
    ├── mdi_homicidios_intencionales_dd_2014_2024.xlsx (93MB)
    ├── mdi_homicidios_intencionales_pm_2014_2024.xlsx (7.4MB)
    └── mdi_homicidiosintencionalse_pm_2025_enero_octubre.xlsx (1.2MB)
```

---

## 🚀 Cómo Ejecutar el Dashboard

### Requisitos
- Python 3.x instalado
- Navegador web moderno (Chrome, Firefox, Edge)

### Pasos

1. **Abrir terminal en la carpeta del proyecto:**
   ```bash
   cd c:\Users\HP\OneDrive\JpE\Github\crimen
   ```

2. **Iniciar servidor HTTP local:**
   ```bash
   python -m http.server 8000
   ```

3. **Abrir navegador y acceder a:**
   ```
   http://localhost:8000/index.html
   ```

> **⚠️ IMPORTANTE:** No abrir el archivo directamente como `file:///` porque causará errores CORS al cargar el CSV.

---

## 🎨 Funcionalidades del Dashboard

### **1. Vista: Serie Histórica**
- **Gráfico de Línea Temporal**: Evolución de homicidios por año o mes
- **Gráfico de Armas**: Top 8 tipos de armas utilizadas (barras horizontales)
- **Distribución Horaria**: Matriz de burbujas mostrando día de la semana vs franja horaria

### **2. Vista: Ranking y Detalle**
- **Pirámide de Víctimas**: 
  - Distribución por edad y sexo
  - Mujeres a la izquierda (rosa), Hombres a la derecha (azul)
  - Edades ordenadas de mayor (80+) arriba a menor (0-4) abajo
  - 17 rangos de edad de 5 años cada uno
  
- **Top Territorios**:
  - Ranking de provincias o cantones con más casos
  - Colores por región:
    - 🟡 Amarillo = Costa (Guayas, Manabí, El Oro, etc.)
    - 🟣 Morado = Sierra (Pichincha, Azuay, Loja, etc.)
    - 🟢 Verde = Amazonía (Sucumbíos, Orellana, etc.)
    - 🔵 Azul = Insular (Galápagos)
  - Botones para alternar entre vista por provincia o cantón

### **3. Vista: Mapa Interactivo**
- **Visualización Híbrida**:
  - 🔥 **Heatmap de concentración**: Gradiente de colores (azul→cyan→verde→amarillo→rojo) mostrando densidad de casos
  - 🔴 **Puntos individuales**: Marcadores rojos clickeables para cada homicidio
  - 🗺️ **Mapa Voyager de CARTO**: Muestra carreteras, autopistas, vías y nombres de calles
  
- **Popups Interactivos**:
  - Al hacer click en cualquier punto rojo se muestra:
    - 📅 Fecha del hecho
    - 🎂 Edad de la víctima
    - 🔫 Arma utilizada
    - 👤 Sexo (con emojis: 👨/👩)
  - Diseño glassmorphism con tema oscuro
  
- **Funcionalidades**:
  - Auto-ajuste de zoom según filtros aplicados
  - Controles de zoom en esquina inferior derecha
  - **Limitación**: Solo disponible para años 2023-2025 (datos con coordenadas)

---

## 🔧 Filtros Globales

Todos disponibles en la barra superior (sticky):

1. **Año**: Todos los años (2014-2025) o individual
2. **Mes**: Todos o específico (1-12)
3. **Provincia**: Multi-selección de provincias
4. **Cantón**: Multi-selección (se actualiza según provincia seleccionada)
5. **Edad**: Rangos predefinidos (Niño, Adolescente, Joven, Adulto, etc.)
6. **Sexo**: Hombre, Mujer, Desconocido
7. **KPI Total**: Indicador en tiempo real del total de casos filtrados

---

## 📊 Detalles Técnicos

### **Tecnologías Utilizadas**

| Tecnología | Propósito |
|------------|-----------|
| **HTML5** | Estructura del dashboard |
| **Tailwind CSS** | Framework CSS (vía CDN) |
| **JavaScript (Vanilla)** | Lógica de aplicación |
| **Chart.js** | Librería de gráficos |
| **ChartDataLabels** | Plugin para etiquetas en gráficos |
| **PapaParse** | Parser de CSV |
| **Leaflet.js** | Mapas interactivos |
| **Leaflet.heat** | Plugin de heatmaps |
| **CARTO Voyager Tiles** | Mapas base con carreteras y vías |

### **Estructura de Datos (CSV)**

Campos principales del archivo `homicidios_clean.csv`:
- `anio`: Año del evento (2014-2025)
- `mes`: Mes del evento (1-12)
- `provincia`: Provincia del evento
- `canton`: Cantón del evento
- `dia_semana`: Día de la semana
- `hora_infraccion`: Hora del evento (0-23)
- `fecha_infraccion`: Fecha completa del evento
- `arma`: Tipo de arma utilizada
- `edad`: Edad de la víctima
- `medida_edad`: Unidad de edad (años, meses, días)
- `sexo`: Sexo de la víctima (HOMBRE, MUJER)
- `rango_edad`: Clasificación etaria (Niño, Adolescente, Joven, etc.)
- `coordenada_x`: Longitud (solo 2023-2025)
- `coordenada_y`: Latitud (solo 2023-2025)

### **Características Especiales del Código**

#### **1. Vista Sensible al Contexto**
```javascript
// El filtro de año se ajusta automáticamente al cambiar a vista de mapa
// Solo años con coordenadas disponibles (2023-2025)
```

#### **2. Actualización Dinámica de Cantones**
```javascript
// Los cantones disponibles se filtran según las provincias seleccionadas
// Mantiene selecciones previas si siguen siendo válidas
```

#### **3. Comparación Multivariable**
El gráfico de línea temporal detecta automáticamente qué comparar:
- Si se seleccionan múltiples provincias → Compara por provincia
- Si se seleccionan múltiples cantones → Compara por cantón
- Si se seleccionan múltiples rangos de edad → Compara por edad
- Si se seleccionan múltiples sexos → Compara por sexo
- Si no hay comparación → Muestra el total agregado

#### **4. Resize Dinámico de Charts**
```javascript
// Cada gráfico tiene un setTimeout que fuerza resize después de creación
// Soluciona problemas de renderizado de Canvas con contenedores dinámicos
```

#### **5. Visualización Híbrida en Mapa**
```javascript
// Dos capas superpuestas:
// 1. Heatmap (L.heatLayer) para densidad/concentración
// 2. CircleMarkers (L.circleMarker) para puntos individuales clickeables
// Permite ver tanto patrones generales como casos específicos
```

---

## 🎨 Diseño Visual

### **Paleta de Colores**

| Uso | Color | Hex |
|-----|-------|-----|
| Primario (Cyan) | ![#22d3ee](https://via.placeholder.com/15/22d3ee/000000?text=+) | `#22d3ee` |
| Hombres | ![#06b6d4](https://via.placeholder.com/15/06b6d4/000000?text=+) | `#06b6d4` |
| Mujeres | ![#ec4899](https://via.placeholder.com/15/ec4899/000000?text=+) | `#ec4899` |
| Armas | ![#f97316](https://via.placeholder.com/15/f97316/000000?text=+) | `#f97316` |
| Morado (Ranking) | ![#a855f7](https://via.placeholder.com/15/a855f7/000000?text=+) | `#a855f7` |
| Puntos Mapa | ![#dc2626](https://via.placeholder.com/15/dc2626/000000?text=+) | `#dc2626` |
| Fondo | ![#0f172a](https://via.placeholder.com/15/0f172a/000000?text=+) | `#0f172a` |

### **Tipografía**
- Fuente: **Outfit** (Google Fonts)
- Pesos: 300 (Light), 400 (Regular), 600 (SemiBold), 700 (Bold)

---

## 📈 Cambios y Mejoras Recientes

### **Sesión 2025-12-07 (Actualización Mayor):**

#### **Mejoras en Mapa:**
1. ✅ **Visualización Híbrida Implementada**
   - Heatmap + marcadores individuales simultáneamente
   - Permite ver patrones de concentración Y casos específicos
   
2. ✅ **Mapa Base Mejorado**
   - Cambiado de "light_all" a "Voyager" de CARTO
   - Ahora muestra carreteras, autopistas y vías de Ecuador
   - Etiquetas de ciudades y nombres de calles visibles al hacer zoom
   
3. ✅ **Popups Interactivos**
   - Click en puntos rojos muestra información detallada
   - Datos mostrados: fecha, edad, arma, sexo
   - Diseño glassmorphism con tema oscuro
   - Estilos personalizados para mejor legibilidad
   
4. ✅ **Corrección de Campos de Datos**
   - Fecha: `fecha_infraccion` (corregido)
   - Sexo: Valores `HOMBRE`/`MUJER` (corregido)
   - Edad: Redondeo automático de decimales
   
5. ✅ **Interfaz Limpia**
   - Eliminado recuadro flotante "Mapa de Calor"
   - Mayor espacio visual para el mapa

#### **Mejoras Previas:**
6. ✅ **Solucionado error CORS** al cargar CSV
   - Implementado servidor HTTP local en vez de file:///
   
7. ✅ **Corregidos gráficos vacíos** en "Ranking y Detalle"
   - Agregado `chart.resize()` con setTimeout post-creación
   
8. ✅ **Invertido orden de edades** en pirámide
   - Mayores (80+) arriba, menores (0-4) abajo
   
9. ✅ **Invertida posición de sexos** en pirámide
   - Mujeres a la izquierda (valores negativos)
   - Hombres a la derecha (valores positivos)
   
10. ✅ **Deshabilitadas etiquetas de valores** en pirámide
    - Tooltips siguen activos al hover
    
11. ✅ **Ajustado tamaño de gráficos** en "Ranking y Detalle"
    - Grid cambiado de 3 columnas (33%/66%) a 2 columnas (50%/50%)
    - Ambos gráficos ahora simétricos
    
12. ✅ **Emoji en Footer**
    - Cambiado de ❤️ a 🧠

---

## 🗂️ Fuentes de Datos

### **Origen**
Ministerio del Interior del Ecuador (MDI)

### **Archivos Base**
1. `mdi_homicidios_intencionales_dd_2014_2024.xlsx` (93 MB)
2. `mdi_homicidios_intencionales_pm_2014_2024.xlsx` (7.4 MB)
3. `mdi_homicidiosintencionalse_pm_2025_enero_octubre.xlsx` (1.2 MB)

### **Procesamiento**
Los datos fueron consolidados y limpiados creando:
- `homicidios_consolidado.csv`
- `homicidios_clean.csv` (usado por el dashboard)

Total de registros: **~38,000 casos** (2014-2025)

---

## 🐛 Problemas Conocidos

1. **Mapa limitado a 2023-2025**
   - Los datos anteriores no tienen coordenadas geográficas
   
2. **Rendimiento con filtros complejos**
   - Cargar "Todos" los años y provincias puede ser lento en navegadores antiguos
   
3. **Tamaño del CSV**
   - 14 MB puede tardar en cargar en conexiones lentas

---

## 🔮 Mejoras Futuras Sugeridas

- [ ] Implementar carga lazy/paginada del CSV
- [ ] Agregar exportación de datos filtrados (Excel/CSV)
- [ ] Incluir análisis de tendencias (crecimiento año a año)
- [ ] Agregar comparación de períodos (2020 vs 2024)
- [ ] Implementar modo offline con Service Workers
- [ ] Agregar gráficos de correlación (hora vs tipo de arma)
- [ ] Incluir predicciones/proyecciones con ML

---

## 👤 Autor

**Proyecto desarrollado para análisis de seguridad ciudadana en Ecuador**

## 📅 Última Actualización

Diciembre 7, 2025

---

## 📝 Notas Adicionales

### **Para Desarrollo Futuro**

Si necesitas modificar visualizaciones:
- Los gráficos están en `app.js` en funciones `render*()` (renderTimeline, renderDemographics, etc.)
- La configuración de colores regionales está en `renderGeoRanking()` en el objeto `regionColors`
- Los bins de edad para la pirámide están definidos al inicio de `renderDemographics()`

### **Para Publicación en GitHub Pages**

1. Crear repositorio en GitHub
2. Subir todos los archivos (HTML, JS, CSS, CSV)
3. Activar GitHub Pages en configuración del repo
4. Seleccionar rama `main` y carpeta raíz
5. El dashboard estará disponible en `https://[usuario].github.io/[repo]/`

---

**¡Dashboard listo para uso y análisis!** 🚀
