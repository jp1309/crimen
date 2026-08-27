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
  ├─ si el portal bloquea la IP del runner, usa SOURCE_HTTPS_PROXY
  ├─ descarga y valida los dos XLSX oficiales
  ├─ compara SHA-256 con las fuentes versionadas
  ├─ reconstruye y verifica ambos CSV cuando hay cambios
  ├─ ejecuta las pruebas unitarias
  ├─ crea un único commit y hace push a main
  └─ publica y comprueba el CSV de GitHub Pages
```

El portal de Datos Abiertos Ecuador responde HTTP 403 a los runners Linux, macOS y Windows de GitHub, incluso cuando usan Cloudflare WARP. También se verificó que un Cloudflare Worker y proxies públicos de centro de datos reciben 403. Por tanto, un relay serverless convencional no resuelve el bloqueo.

Para mantener la operación completamente remota, el repositorio admite el secreto `SOURCE_HTTPS_PROXY`, con una URL de proxy HTTPS administrado y salida ISP/residencial en formato `http://usuario:contraseña@host:puerto`. El secreto solo se inyecta en los pasos de prueba y descarga; GitHub oculta su valor en los registros. Después de esta configuración única, ninguna ejecución depende de Codex o de una máquina local.

La ruta alternativa no reduce los controles de integridad: los archivos recibidos todavía deben ser XLSX válidos, superar el tamaño mínimo, contener la tabla esperada y producir conteos exactos.

## Eventos

- `schedule`: consulta y actualiza los datos automáticamente.
- `workflow_dispatch`: permite una actualización remota inmediata desde la pestaña Actions.
- `push` sobre scripts, pruebas, dependencias o el propio workflow: reconstruye y valida los datos versionados, pero no consulta la fuente ni crea commits.

Esta separación evita ciclos: el commit automático de datos no dispara una segunda actualización.

## Configuración única requerida por el portal

Mientras el portal mantenga el bloqueo de infraestructura de nube, configure en `Settings → Secrets and variables → Actions`:

| Secreto | Contenido |
|---|---|
| `SOURCE_HTTPS_PROXY` | URL completa de un proxy HTTPS administrado con salida ISP/residencial aceptada por el portal |

El proveedor debe admitir HTTPS CONNECT, credenciales en URL y al menos 100 MB mensuales. Conviene restringir el destino a `www.datosabiertos.gob.ec` si el proveedor ofrece listas permitidas. No use proxies públicos ni relays genéricos: además de ser inestables, no establecen una cadena de confianza operativa adecuada.

Configure el secreto una sola vez:

```bash
gh secret set SOURCE_HTTPS_PROXY --repo jp1309/crimen
```

El comando solicita el valor sin imprimirlo. No guarde la URL ni sus credenciales en el repositorio. Si la ruta directa vuelve a funcionar, el workflow la prefiere y no utiliza el secreto.

## Controles obligatorios

Una actualización solo se publica si:

1. Ambos recursos son XLSX válidos de más de 50 KB.
2. Se encuentra una tabla oficial con `PROVINCIA`.
3. El histórico y el año actual no contienen años solapados.
4. Los conteos de los Excel y del CSV coinciden exactamente por año.
5. Terminan correctamente las verificaciones geográficas y las pruebas unitarias.
6. El commit incluye exclusivamente los cinco artefactos de datos autorizados.
7. GitHub Pages sirve un CSV cuyo SHA-256 coincide con el generado.

GitHub Pages normaliza los saltos CRLF del CSV versionado a LF. La verificación remota normaliza exclusivamente esos saltos antes de comparar SHA-256; no permite ninguna diferencia de datos.

Ante cualquier fallo no se publica un conjunto parcial. La siguiente fecha programada vuelve a intentarlo.

## Supervisión

La pestaña [Actions](https://github.com/jp1309/crimen/actions/workflows/update_data.yml) contiene el historial completo, incluidos los intentos sin cambios y los errores de red. El badge del README refleja el estado del último workflow.

Si una ejecución programada o manual falla, el job `Registrar incidente de automatizacion` crea un issue único o agrega la nueva ejecución al incidente ya abierto. Cuando el workflow vuelve a terminar correctamente, `Cerrar incidente recuperado` comenta y cierra ese issue. Así los fallos repetidos son visibles sin crear ruido duplicado.

Para forzar una revisión remota:

1. Abra `Actions`.
2. Seleccione `Actualizar datos y dashboard`.
3. Use `Run workflow` sobre `main`.
4. Compruebe los pasos de sincronización, validación, commit y publicación.
