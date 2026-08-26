# Documentación del proyecto

Este directorio reúne la documentación técnica y operativa del Observatorio de Seguridad. El `README.md` de la raíz funciona como introducción; estos documentos explican cómo mantener el sistema sin depender de conocimiento informal.

| Documento | Para qué sirve | Cuándo consultarlo |
|---|---|---|
| [Automatización](AUTOMATIZACION.md) | Cron, descarga remota, validación, commit y publicación en GitHub Actions | Al cambiar horario, fuente o mecanismo de despliegue |
| [Operación y recuperación](OPERACION_Y_RECUPERACION.md) | Ejecución manual, diagnóstico, publicación, cierre anual y reversión | Ante una actualización o un fallo |
| [Diccionario de datos](DICCIONARIO_DATOS.md) | Granularidad, columnas, tipos, valores faltantes y campos derivados | Al analizar datos o modificar el ETL |
| [Arquitectura del frontend](ARQUITECTURA_FRONTEND.md) | Flujo del navegador, vistas, dependencias y puntos de extensión | Al modificar el dashboard |
| [Guía de contribución](../CONTRIBUTING.md) | Reglas para cambios de código y datos | Antes de preparar un commit |

## Fuente de verdad por tema

- Fuente oficial descargada: `data/source_manifest.json`.
- Archivos que procesa el ETL: `scripts/configuracion.py`.
- Transformaciones: `scripts/consolidar_y_limpiar.py` y `scripts/limpiar_datos.py`.
- Invariantes obligatorios: `scripts/verificar_datos.py`.
- Automatización remota vigente: workflow `Actualizar datos y dashboard` en GitHub Actions.
- Reconstrucción y publicación remota: `.github/workflows/update_data.yml`.

Si la documentación y el código difieren, debe corregirse la documentación en el mismo cambio que modifica el comportamiento.
