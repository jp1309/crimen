# Automatización mensual

## Objetivo

La automatización detecta una nueva publicación oficial, reemplaza las fuentes acumulativas, reconstruye todos los datos, ejecuta controles de calidad y publica el dashboard. No agrega solamente el último mes: vuelve a procesar el año completo para incorporar correcciones retroactivas del Ministerio.

## Configuración vigente

| Propiedad | Valor |
|---|---|
| Nombre | `Actualizar dashboard de homicidios` |
| Identificador | `actualizar-dashboard-de-homicidios` |
| Estado esperado | Activa |
| Entorno | Local, asociado al proyecto `crimen` |
| Rama de publicación | `main` |
| Hora | 09:17, hora local del entorno de Codex |
| Días de ejecución | 2, 5, 8, 11, 15, 18, 21, 24, 27 y 30 de cada mes |

Los días 15, 18, 21, 24, 27 y 30 buscan la publicación esperada del mes. Los días 2, 5, 8 y 11 permiten continuar los reintentos si el Ministerio se retrasa hasta el mes siguiente. Cada intento es idempotente: si los archivos oficiales no cambiaron, no crea un commit.

La zona horaria pertenece al entorno local de Codex. Al migrar a otro equipo debe comprobarse la zona horaria antes de activar la tarea.

## Distribución de responsabilidades

```text
Automatización local de Codex
  ├─ consulta y descarga desde Datos Abiertos Ecuador
  ├─ valida los XLSX y compara SHA-256
  ├─ reconstruye y verifica el CSV cuando existe un cambio
  └─ crea un commit y hace push a main
                    │
                    ▼
GitHub Actions
  ├─ reconstruye desde las fuentes versionadas
  ├─ repite las validaciones
  └─ solicita/acompaña la publicación en GitHub Pages
                    │
                    ▼
Dashboard público
```

La descarga se realiza localmente porque el portal oficial puede bloquear las direcciones de los runners alojados por GitHub. GitHub Actions nunca debe convertirse en la única vía de descarga.

## Instrucción operativa de la tarea

La tarea debe usar la siguiente instrucción. Se conserva aquí para poder reconstruirla si se elimina o se migra el proyecto:

> Actualiza y publica automáticamente los datos del dashboard de homicidios en este proyecto. Trabaja exclusivamente dentro del repositorio `crimen`. Primero revisa `git status` y preserva todos los archivos no rastreados o cambios ajenos; nunca incluyas imágenes, videos, ZIP ni otros artefactos no relacionados. Sincroniza `main` con `origin/main` mediante un avance rápido seguro. Instala `requirements.txt` si hace falta. Ejecuta `python -m scripts.descargar_datos`. Si las dos fuentes canónicas y `data/source_manifest.json` no cambian, no reconstruyas, no hagas commit ni push; informa que todavía no existe una publicación nueva. Si existe una actualización, ejecuta `python -m scripts.consolidar_y_limpiar`, `python -m scripts.verificar_datos`, `python -m scripts.verificar_coordenadas` y `python -m unittest discover -v`. Solo si todo pasa, prepara explícitamente `data/raw/mdi_homicidios_intencionales_pm_actual.xlsx`, `data/raw/mdi_homicidios_intencionales_pm_historico.xlsx`, `data/source_manifest.json`, `data/processed/homicidios_consolidado.csv` y `homicidios_clean.csv`; crea un commit conciso y haz push a `main`. Después sigue el workflow `Actualizar datos y dashboard` y la publicación de GitHub Pages hasta que ambos terminen correctamente. Verifica que `https://jp1309.github.io/crimen/` sirva el CSV actualizado. Si el portal o GitHub presentan un error transitorio, no alteres datos ni crees commits incompletos; deja fallar la ejecución para que el siguiente intento programado pueda reintentar.

## Cómo recrearla

1. Abrir en Codex el proyecto cuya carpeta sea este repositorio.
2. Crear una automatización recurrente local con el nombre `Actualizar dashboard de homicidios`.
3. Configurar las ejecuciones a las 09:17 los días 2, 5, 8, 11, 15, 18, 21, 24, 27 y 30.
4. Copiar la instrucción operativa anterior sin eliminar los límites de seguridad.
5. Confirmar que la tarea se ejecute en la carpeta del repositorio y tenga acceso a Python, Git y GitHub CLI.
6. Activarla y ejecutar una primera revisión supervisada.
7. Si no existe una publicación nueva, comprobar que termine sin commit. Si existe, comprobar el ciclo completo descrito en [Operación y recuperación](OPERACION_Y_RECUPERACION.md).

## Precondiciones del equipo local

- El repositorio debe conservar el remoto `origin` de GitHub y la rama `main`.
- Python 3.10 o superior debe estar disponible.
- GitHub CLI debe estar autenticado con permiso para hacer push y consultar Actions/Pages.
- El entorno local de Codex debe poder iniciar la tarea programada y acceder a internet.
- No debe existir otra automatización que actualice simultáneamente los mismos archivos.

Comprobaciones rápidas:

```bash
python --version
git remote -v
git branch --show-current
gh auth status
```

## Resultados esperados

### Sin publicación nueva

- El sincronizador informa `Cambios detectados: no`.
- No se reconstruyen archivos.
- No se crea commit ni se ejecuta `push`.
- El siguiente intento programado vuelve a consultar la fuente.

### Con publicación nueva

- Cambian uno o ambos XLSX canónicos y `data/source_manifest.json`.
- Se reconstruyen ambos CSV desde cero.
- Pasan integridad, coordenadas y pruebas unitarias.
- El commit contiene exclusivamente los cinco archivos de datos permitidos.
- El workflow remoto y la publicación terminan correctamente.
- El CSV público coincide con la versión publicada en `main`.

### Con error

- No se debe crear un commit parcial.
- Los archivos oficiales se reemplazan de forma atómica; un fallo de descarga no debe destruir las copias válidas.
- El incidente queda visible como ejecución fallida y el próximo día programado reintenta.
- Si el error se repite, seguir la matriz de [Operación y recuperación](OPERACION_Y_RECUPERACION.md#matriz-de-diagnóstico).

## Cambios que obligan a actualizar este documento

- Horario, zona horaria o días de ejecución.
- Nombre, identificador, entorno o instrucción de la automatización.
- Rama o mecanismo de despliegue.
- Lista de archivos autorizados para el commit.
- Cambio del portal o de los recursos oficiales.
