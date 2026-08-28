# Operación y recuperación

## Flujo normal

La vía normal es la tarea local de Codex descrita en [AUTOMATIZACION.md](AUTOMATIZACION.md). Codex ejecuta este mismo procedimiento, publica únicamente cuando detecta fuentes nuevas y sigue la validación remota hasta GitHub Pages.

## Reintento supervisado

Solicite la actualización desde el proyecto `crimen` en Codex. GitHub Actions no descarga la fuente oficial: `Run workflow` solo reconstruye y valida los archivos ya versionados.

## Actualización manual segura

### 1. Preparar el repositorio

```bash
git status --short
git switch main
git pull --ff-only origin main
python -m pip install --requirement requirements.txt
```

No continúe si hay cambios propios que se solapan con los cinco archivos de datos del pipeline. Los archivos no relacionados deben preservarse y nunca incluirse por accidente.

### 2. Consultar y descargar

```bash
python -m scripts.descargar_datos
```

Si la salida indica `Cambios detectados: no`, el proceso termina aquí. No haga commit.

Para comprobar la fuente sin reemplazar los archivos locales:

```bash
python -m scripts.descargar_datos --dry-run
```

### 3. Reconstruir y validar

```bash
python -m scripts.consolidar_y_limpiar
python -m scripts.verificar_datos
python -m scripts.verificar_coordenadas
python -m unittest discover -v
```

`verificar_datos` es un bloqueo obligatorio: exige igualdad exacta entre los Excel y el CSV por total y por año. `verificar_coordenadas` es un diagnóstico de cobertura; actualmente informa la proporción, pero no aplica un umbral mínimo. Las pruebas unitarias validan selección de recursos, validación XLSX, reemplazo acumulativo e idempotencia.

### 4. Revisar y publicar

```bash
git status --short
git diff --stat
git add -- data/raw/mdi_homicidios_intencionales_pm_actual.xlsx data/raw/mdi_homicidios_intencionales_pm_historico.xlsx data/source_manifest.json data/processed/homicidios_consolidado.csv homicidios_clean.csv
git diff --staged --stat
git commit -m "Actualizar datos oficiales de homicidios"
git push origin main
```

La revisión del área preparada debe contener exclusivamente los archivos anteriores. Si algún control falló, no publique.

### 5. Comprobar GitHub y el sitio

```bash
gh run list --workflow update_data.yml --limit 5
gh run watch --exit-status
```

Luego compruebe:

- El workflow `Actualizar datos y dashboard` terminó correctamente.
- GitHub Pages publicó el commit nuevo.
- [El dashboard](https://jp1309.github.io/crimen/) carga sin errores.
- [El CSV público](https://jp1309.github.io/crimen/homicidios_clean.csv) contiene la fecha máxima y el total esperados.

## Matriz de diagnóstico

| Síntoma | Causa probable | Acción segura |
|---|---|---|
| HTTP 403 al consultar CKAN | El portal bloqueó temporalmente el acceso local | No sustituir la fuente ni usar proxies públicos; dejar el intento fallido para que la tarea local vuelva a consultar |
| Tiempo de espera o error DNS | Incidente transitorio de red o portal | Ejecutar `--dry-run` más tarde; no sustituir los XLSX manualmente |
| Archivo menor a 50 KB o XLSX inválido | Respuesta HTML, descarga incompleta o formato oficial roto | Conservar las fuentes locales; inspeccionar la publicación y adaptar una prueba antes del código |
| No se detecta una tabla con `PROVINCIA` | Cambió la hoja o la fila de encabezado | Revisar el Excel nuevo, ajustar la detección y agregar una prueba representativa |
| Años solapados entre histórico y actual | Transición anual inconsistente del portal o clasificación incorrecta | Detener el proceso; no eliminar filas ni deduplicar a mano. Esperar una publicación coherente o corregir la selección de fuentes |
| Total o conteo anual distinto | Transformación que perdió, duplicó o alteró filas | No publicar. Comparar primero el consolidado con cada Excel y revisar `limpiar_datos.py` |
| Baja cobertura de coordenadas | La fuente usa ceros o no georreferencia algunos periodos | El dashboard sigue siendo válido para análisis no espaciales; documentar la cobertura y no inventar coordenadas |
| Pruebas unitarias fallidas | Cambio incompatible en descarga o validación | Corregir código/prueba antes del commit; no omitir el control |
| Rechazo de `git pull --ff-only` | Rama local y remota divergieron | Inspeccionar `git log --oneline --graph --all`; resolver conscientemente sin usar `reset --hard` |
| Push rechazado | Permisos, autenticación o rama remota adelantada | Ejecutar `gh auth status`, actualizar con avance rápido y reintentar solo tras revisar el diff |
| Workflow fallido | Dependencias, QA o permisos de GitHub | Abrir el paso fallido, reproducirlo localmente y corregir antes de relanzar |
| Workflow correcto pero sitio antiguo | Build de Pages pendiente o fallido | Revisar `Deployments`/Pages, relanzar el build y verificar el CSV público antes de declarar éxito |

## Transición de año

Al comenzar un año nuevo, el portal debería mover el año cerrado al histórico y publicar un nuevo acumulado anual. El pipeline exige que ambos archivos no compartan años.

Checklist de transición:

1. Confirmar en `data/source_manifest.json` los nombres oficiales y fechas de modificación.
2. Ejecutar la descarga y comprobar qué años contiene cada XLSX.
3. Verificar que el histórico termine en el año cerrado y el actual contenga únicamente el año nuevo.
4. Ejecutar reconstrucción, integridad y pruebas completas.
5. Confirmar que el total histórico anterior se mantiene, salvo revisiones oficiales explícitas.
6. No cambiar los nombres canónicos locales: son deliberadamente estables.

Si el portal publica temporalmente el año cerrado en ambos archivos, el pipeline debe fallar. Esta es una protección, no un error que deba evitarse eliminando datos.

## Reversión de una publicación incorrecta

Si una actualización incorrecta llegó a `main`, preserve el historial y revierta el commit completo:

```bash
git log --oneline --max-count=10
git revert <commit-de-la-actualizacion>
git push origin main
```

Después siga GitHub Actions y Pages hasta que el sitio vuelva a servir la versión anterior. No use `git reset --hard` ni reescriba la historia de `main`.

Antes de volver a publicar los datos corregidos, determine si el problema estaba en la fuente oficial, en el ETL o en el despliegue.

## Información mínima de un incidente

Conserve en el reporte:

- Fecha y hora del intento.
- Nombre oficial, `last_modified`, tamaño y SHA-256 de cada recurso.
- Comando y mensaje de error completo.
- Commit local y commit público, si existen.
- Resultado de integridad, coordenadas y pruebas.
- URL/identificador de la ejecución de GitHub Actions.
- Estado del CSV público.

No incluya tokens, credenciales ni datos personales adicionales en el reporte.
