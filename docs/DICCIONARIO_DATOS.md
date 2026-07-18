# Diccionario de datos

## Alcance y granularidad

`homicidios_clean.csv` es la interfaz de datos del dashboard. Cada fila representa un registro individual publicado por el Ministerio del Interior dentro del conjunto de homicidios intencionales. El archivo no contiene un identificador único de evento; por ello no deben inferirse relaciones entre filas ni deduplicarse registros sin contrastar la fuente oficial.

La cobertura temporal y el número de filas cambian con cada publicación mensual. Use `data/source_manifest.json` para identificar las fuentes exactas de una versión y `python -m scripts.verificar_datos` para obtener el total vigente por año.

## Convenciones

- Codificación: UTF-8; separador coma; primera fila con encabezados.
- Los nombres de columna se convierten a minúsculas y los espacios a guiones bajos.
- `fecha_infraccion` se exporta en formato ISO `AAAA-MM-DD`.
- `coordenada_x` es longitud y `coordenada_y` es latitud.
- Las coordenadas `0, 0` se consideran ausentes para el análisis espacial, aunque estén presentes como números en el CSV.
- En las columnas textuales normalizadas se aplican mayúsculas, eliminación de tildes y espacios exteriores.
- Según la columna y la fuente, la ausencia puede aparecer como vacío, `SIN_DATO`, `NO DETERMINADO` o `DESCONOCIDO`. No se deben fusionar estas categorías sin una decisión analítica explícita.
- `edad` y `rango_edad` pueden estar vacíos cuando la fuente no contiene una edad numérica válida.
- Los códigos territoriales se conservan como los entrega la fuente; no sustituyen una tabla oficial de divisiones administrativas.

## Columnas

| Columna | Tipo en el CSV | Origen | Descripción |
|---|---|---|---|
| `tipo_muerte` | texto | Oficial | Clasificación del registro: homicidio, asesinato, femicidio o sicariato, según la fuente |
| `zona` | texto | Oficial | Zona administrativa/policial |
| `subzona` | texto | Oficial | Subzona administrativa/policial |
| `distrito` | texto | Oficial | Distrito administrativo/policial |
| `circuito` | texto | Oficial | Circuito administrativo/policial |
| `codigo_subcircuito` | texto | Oficial | Código del subcircuito; se trata como texto para preservar su forma |
| `subcircuito` | texto | Oficial | Nombre del subcircuito |
| `codigo_provincia` | entero | Oficial | Código de provincia publicado en el archivo fuente |
| `provincia` | texto | Oficial normalizado | Provincia del registro |
| `codigo_canton` | entero | Oficial | Código de cantón publicado en el archivo fuente |
| `canton` | texto | Oficial normalizado | Cantón; además corrige tres variantes ortográficas conocidas en el ETL |
| `coordenada_y` | decimal | Oficial normalizado | Latitud del registro; cero significa que no hay coordenada utilizable |
| `coordenada_x` | decimal | Oficial normalizado | Longitud del registro; cero significa que no hay coordenada utilizable |
| `area_hecho` | texto | Oficial | Área urbana, rural o sin dato |
| `lugar` | texto | Oficial | Descripción específica del lugar del hecho |
| `tipo_lugar` | texto | Oficial normalizado | Clasificación general del lugar como público o privado |
| `fecha_infraccion` | fecha | Oficial normalizado | Fecha de la infracción |
| `hora_infraccion` | texto/hora | Oficial | Hora reportada; el frontend la interpreta para distribuciones horarias |
| `arma` | texto | Oficial normalizado | Familia general del arma o mecanismo |
| `tipo_arma` | texto | Oficial | Descripción específica del arma o mecanismo |
| `presunta_motivacion` | texto | Oficial | Categoría general de motivación presunta |
| `presun_motiva_observada` | texto | Oficial | Motivación observada con el nombre de columna conservado de la fuente |
| `probable_causa_motivada` | texto | Oficial | Causa probable reportada por la fuente |
| `edad` | decimal anulable | Oficial normalizado | Edad convertida a número; valores no numéricos se transforman en vacío |
| `medida_edad` | texto | Oficial | Unidad o indicador asociado a la edad en la fuente |
| `sexo` | texto | Oficial normalizado | Sexo reportado |
| `genero` | texto | Oficial | Género reportado |
| `etnia` | texto | Oficial | Etnia reportada |
| `estado_civil` | texto | Oficial normalizado | Estado civil reportado |
| `nacionalidad` | texto | Oficial normalizado | Nacionalidad reportada |
| `discapacidad` | texto | Oficial | Discapacidad reportada o categoría de ausencia |
| `profesion_registro_civil` | texto | Oficial | Profesión registrada en la fuente administrativa |
| `instruccion` | texto | Oficial | Nivel de instrucción reportado |
| `anio` | entero | Derivado | Año extraído de `fecha_infraccion` |
| `mes` | entero | Derivado | Mes de 1 a 12 extraído de `fecha_infraccion` |
| `dia_semana` | texto | Derivado | Día de la semana calculado en español |
| `rango_edad` | categoría anulable | Derivado | Grupo de edad calculado según los intervalos descritos abajo |

## Campos derivados

### Fecha

```text
fecha_infraccion
  ├─ anio
  ├─ mes
  └─ dia_semana
```

Una fecha que no pueda interpretarse produciría valores derivados vacíos. La validación de integridad actual impide publicar fuentes con fechas inválidas.

### Rangos de edad

| Rango | Intervalo utilizado |
|---|---:|
| Niño | 0–11 años |
| Adolescente | 12–17 años |
| Joven | 18–29 años |
| Adulto | 30–49 años |
| Adulto Mayor | 50–64 años |
| Anciano | 65–99 años |

Los intervalos incluyen el límite inferior y excluyen el superior. Una edad ausente, no numérica, negativa o igual/superior a 100 queda sin `rango_edad`.

## Normalizaciones aplicadas

El ETL normaliza estas columnas textuales cuando existen:

```text
provincia, canton, parroquia, sexo, estado_civil,
nacionalidad, tipo_muerte, arma, tipo_lugar, zona
```

Además reemplaza las siguientes variantes de cantón:

| Valor de origen | Valor normalizado |
|---|---|
| `ALFREDO BAQUERIZO MORENO (JUJAN)` | `ALFREDO BAQUERIZO MORENO` |
| `CRNEL. MARCELINO MARIDUENA` | `CORONEL MARCELINO MARIDUENA` |
| `GNRAL. ANTONIO ELIZALDE` | `GENERAL ANTONIO ELIZALDE` |

Las demás columnas textuales conservan las categorías de la fuente, salvo la normalización del nombre de columna.

## Controles relacionados

| Control | Qué garantiza | Comando |
|---|---|---|
| Integridad | Igualdad exacta de filas y conteos anuales entre los XLSX y el CSV | `python -m scripts.verificar_datos` |
| Coordenadas | Reporte de registros con coordenadas distintas de cero por año | `python -m scripts.verificar_coordenadas` |
| Cantones | Detección exploratoria de variantes por tildes/ortografía | `python -m scripts.verificar_cantones` |

## Uso responsable

El archivo no contiene nombres ni números de identificación, pero combina fecha, ubicación y atributos demográficos. Para publicaciones analíticas se recomienda agregar los resultados y evitar exponer combinaciones con muy pocos registros. Las categorías de motivación, causa, género, etnia y discapacidad son las reportadas por la fuente y no deben reinterpretarse como determinaciones judiciales.

## Cambio de esquema

Si la fuente agrega, elimina o cambia una columna:

1. Conservar una muestra del nuevo formato para una prueba.
2. Actualizar el ETL y sus columnas obligatorias.
3. Actualizar este diccionario en el mismo commit.
4. Reconstruir desde ambos XLSX.
5. Ejecutar todos los controles y comprobar el frontend.
