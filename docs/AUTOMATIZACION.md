# Automatización mensual supervisada

## Objetivo

La actualización usa una tarea local de Codex asociada a este proyecto. Codex consulta las fuentes oficiales, ejecuta el pipeline y, si encuentra datos nuevos y todos los controles pasan, crea un commit acotado y lo publica en `main`.

Esta arquitectura no utiliza proxies, relays ni servicios de pago. La computadora que contiene el repositorio debe estar disponible durante la ejecución programada.

## Configuración vigente

| Propiedad | Valor |
|---|---|
| Tarea de Codex | `Actualizar dashboard de homicidios` |
| Entorno | Local, dentro del proyecto `crimen` |
| Rama de publicación | `main` |
| Hora | 09:17, `America/New_York` |
| Días | 2, 5, 8, 11, 15, 18, 21, 24, 27 y 30 |
| Verificación remota | Workflow `Actualizar datos y dashboard` |

Los intentos son idempotentes. Si los archivos oficiales conservan los mismos SHA-256, la tarea termina sin reconstruir, crear commits ni publicar.

## Flujo

```text
Automatización local de Codex
  ├─ sincroniza main por avance rápido seguro
  ├─ preserva todos los cambios y artefactos ajenos
  ├─ descarga y valida los dos XLSX oficiales
  ├─ compara SHA-256 con las fuentes versionadas
  ├─ reconstruye y verifica ambos CSV cuando hay cambios
  ├─ ejecuta las pruebas unitarias
  ├─ prepara únicamente los cinco archivos canónicos
  ├─ crea un commit y hace push a main
  └─ sigue GitHub Actions y GitHub Pages hasta verificar el CSV público
```

El portal de Datos Abiertos Ecuador puede bloquear direcciones de centros de datos, incluidos los runners de GitHub. Por esa razón GitHub Actions no intenta descargar las fuentes: la consulta ocurre desde el entorno local de Codex, que ya ha demostrado acceso al portal cuando este está disponible.

## Separación de responsabilidades

- Codex local: consulta la fuente, detecta cambios, reconstruye, valida, crea el commit y hace `push`.
- GitHub Actions: reconstruye y valida los datos ya versionados en cada `push` relevante. No modifica el repositorio.
- GitHub Pages: publica `main`; Codex comprueba que el CSV público corresponde al commit nuevo.

El workflow remoto también admite `workflow_dispatch` para volver a verificar manualmente el estado versionado, pero no descarga información oficial.

## Controles obligatorios

Una actualización solo se publica si:

1. Ambos recursos son XLSX válidos de más de 50 KB.
2. Se encuentra una tabla oficial con `PROVINCIA`.
3. El histórico y el año actual no contienen años solapados.
4. Los conteos de los Excel y del CSV coinciden exactamente por año.
5. Terminan correctamente las verificaciones geográficas y las pruebas unitarias.
6. El commit incluye exclusivamente los cinco artefactos de datos autorizados.
7. GitHub Actions termina correctamente y GitHub Pages sirve el CSV esperado.

Ante un fallo del portal o de GitHub no se publica un conjunto parcial. La tarea informa el incidente en Codex y el siguiente intento programado vuelve a consultar.

## Supervisión

Los resultados de la tarea aparecen en Codex. La pestaña [Actions](https://github.com/jp1309/crimen/actions/workflows/update_data.yml) contiene la validación de cada publicación, y el dashboard queda disponible en [GitHub Pages](https://jp1309.github.io/crimen/).

Para solicitar una revisión inmediata, abra este proyecto en Codex y pida actualizar el dashboard. El procedimiento operativo detallado está en [OPERACION_Y_RECUPERACION.md](OPERACION_Y_RECUPERACION.md).
