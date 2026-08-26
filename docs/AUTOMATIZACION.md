# Automatización remota mensual

## Objetivo

La actualización se ejecuta íntegramente en GitHub Actions. No depende de Codex, de una computadora encendida ni de una tarea programada fuera del repositorio.

## Configuración vigente

| Propiedad | Valor |
|---|---|
| Workflow | `Actualizar datos y dashboard` |
| Archivo | `.github/workflows/update_data.yml` |
| Entorno | GitHub-hosted runner `ubuntu-24.04` |
| Rama de publicación | `main` |
| Hora | 09:17, `America/New_York` |
| Días | 2, 5, 8, 11, 15, 18, 21, 24, 27 y 30 |
| Ejecución manual | `workflow_dispatch` |

Los intentos son idempotentes. Si los archivos oficiales conservan los mismos SHA-256, el workflow termina sin commit y vuelve a consultar en la siguiente fecha.

## Flujo remoto

```text
GitHub Actions (schedule o workflow_dispatch)
  ├─ prueba acceso directo al recurso oficial
  ├─ si el portal bloquea la IP del runner, activa Cloudflare WARP
  ├─ descarga y valida los dos XLSX oficiales
  ├─ compara SHA-256 con las fuentes versionadas
  ├─ reconstruye y verifica ambos CSV cuando hay cambios
  ├─ ejecuta las pruebas unitarias
  ├─ crea un único commit y hace push a main
  └─ publica y comprueba el CSV de GitHub Pages
```

El portal de Datos Abiertos Ecuador ha respondido HTTP 403 a direcciones de GitHub. Para mantener la operación completamente remota, el workflow instala el cliente oficial de Cloudflare WARP únicamente cuando falla la ruta directa. La instalación usa el repositorio firmado de Cloudflare y no requiere secretos ni infraestructura propia.

## Eventos

- `schedule`: consulta y actualiza los datos automáticamente.
- `workflow_dispatch`: permite una actualización remota inmediata desde la pestaña Actions.
- `push` sobre scripts, pruebas, dependencias o el propio workflow: reconstruye y valida los datos versionados, pero no consulta la fuente ni crea commits.

Esta separación evita ciclos: el commit automático de datos no dispara una segunda actualización.

## Controles obligatorios

Una actualización solo se publica si:

1. Ambos recursos son XLSX válidos de más de 50 KB.
2. Se encuentra una tabla oficial con `PROVINCIA`.
3. El histórico y el año actual no contienen años solapados.
4. Los conteos de los Excel y del CSV coinciden exactamente por año.
5. Terminan correctamente las verificaciones geográficas y las pruebas unitarias.
6. El commit incluye exclusivamente los cinco artefactos de datos autorizados.
7. GitHub Pages sirve un CSV cuyo SHA-256 coincide con el generado.

Ante cualquier fallo no se publica un conjunto parcial. La siguiente fecha programada vuelve a intentarlo.

## Supervisión

La pestaña [Actions](https://github.com/jp1309/crimen/actions/workflows/update_data.yml) contiene el historial completo, incluidos los intentos sin cambios y los errores de red. El badge del README refleja el estado del último workflow.

Para forzar una revisión remota:

1. Abra `Actions`.
2. Seleccione `Actualizar datos y dashboard`.
3. Use `Run workflow` sobre `main`.
4. Compruebe los pasos de sincronización, validación, commit y publicación.
