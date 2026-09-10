---
slug: task-batch-duplicate-filenames
epic: epic-converter
title: "[Bug] Batch PDF→JPG pisa archivos cuando 2+ PDFs tienen el mismo nombre"
type: tech-task
labels: type:tech-task, area:converter, P1, gate:listo-para-build
milestone: MixTools v1
---
## Bug encontrado
Al subir 2 PDFs con el **mismo nombre de archivo** (ej. dos "recibo.pdf" de
carpetas distintas) al endpoint batch, solo se genera **una** carpeta/imagen
en el zip resultante — el segundo pisa al primero en vez de conservarse
ambos. Encontrado en QA manual de #21 sobre la lógica de #17.

## Comportamiento esperado
Igual que hacen los navegadores/sistemas de archivos al bajar un archivo
duplicado: agregar un sufijo numérico incremental al nombre en colisión.

- 1er PDF llamado "recibo.pdf", 1 página → `recibo.jpg`
- 2do PDF también llamado "recibo.pdf", 1 página → `recibo (1).jpg`
- Si hay un tercero → `recibo (2).jpg`, y así
- Mismo criterio para carpetas (PDFs de 2+ páginas): `recibo/`,
  `recibo (1)/`, `recibo (2)/`

## Tasks
- [ ] En `batch_pdfs_to_jpg_zip` (`backend/app/tools/converter/engine.py`),
      llevar un registro de nombres ya usados (carpetas e imágenes sueltas
      por separado) y aplicar el sufijo `(N)` ante colisión, antes de
      escribir al zip.
- [ ] Test: subir 2 PDFs con el mismo nombre (uno de 1 página, uno de 3) →
      confirmar que el zip contiene AMBOS resultados, con el sufijo
      aplicado al segundo.
- [ ] Test: 3 PDFs con el mismo nombre → confirmar `(1)` y `(2)`
      correlativos, ninguno se pisa.

## Acceptance
- [ ] `uv run pytest backend/tests/converter/test_engine.py -k batch` sigue
      pasando (no rompe los tests existentes) + el/los tests nuevos de
      colisión de nombres pasan
- [ ] Probado a mano: 2 PDFs reales con el mismo nombre → 2 resultados
      distintos en el zip, no 1

## Fuera de scope
Cualquier cambio al endpoint single-file (`/pdf-a-jpg`) — ese no tiene este
problema porque siempre es un solo PDF.
