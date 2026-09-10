---
slug: task-fix-save-upload-collision
epic: epic-infra
title: "[Bug] save_upload pisa archivos en disco cuando 2+ uploads comparten nombre (afecta merge, jpg-a-pdf, batch-pdf-a-jpg)"
type: tech-task
labels: type:tech-task, area:infra, P0, gate:listo-para-build
milestone: MixTools v1
---
## Bug encontrado
`save_upload()` (`backend/app/utils/files.py`) guarda cada archivo subido
como `dest_dir / upload_file.filename` — siempre el mismo `dest_dir` (el
workspace de la request). Cuando un endpoint acepta varios archivos y dos
comparten nombre, el segundo **pisa al primero en el disco** antes de que
cualquier lógica de negocio llegue a verlos. El fix de nombres duplicados
de #23/#24 resuelve la colisión en el zip de salida, pero no puede arreglar
datos que ya llegaron corrompidos por este bug previo.

Afecta a los tres endpoints que reciben `files: list[UploadFile]`:
- `POST /api/converter/merge`
- `POST /api/converter/jpg-a-pdf`
- `POST /api/converter/batch-pdf-a-jpg`

Encontrado en QA manual durante #24 (dos PDFs mismo nombre, distinta
cantidad de páginas → el segundo pisó al primero en disco, el engine nunca
vio el primero).

## Fix propuesto
Cada archivo subido dentro de un mismo request va a su propio subdirectorio
numerado (ej. `ws/000/recibo.pdf`, `ws/001/recibo.pdf`) — preserva el
nombre original (necesario para el nombrado del zip en #24) sin colisionar
en el filesystem.

## Tasks
- [ ] Extender `save_upload()` (o agregar una variante) para aceptar un
      subdirectorio/índice por archivo, sin romper las llamadas existentes
      de un solo archivo (`office-a-pdf`, `pdf-a-jpg`, etc.)
- [ ] Actualizar los 3 loops afectados (`merge`, `jpg-a-pdf`,
      `batch-pdf-a-jpg`) para usar un subdirectorio por archivo
- [ ] Test: 2 PDFs con el mismo nombre subidos a `batch-pdf-a-jpg` con
      distinta cantidad de páginas cada uno → confirmar que el resultado
      final tiene AMBOS conjuntos de páginas correctos (no uno corrompido)
- [ ] Test equivalente para `merge` y `jpg-a-pdf` con archivos de mismo
      nombre — confirmar que no se pierden datos

## Acceptance
- [ ] Los tests existentes de `merge`, `jpg-a-pdf`, `batch-pdf-a-jpg`
      (incluidos los de #17 y #24) siguen pasando
- [ ] Nuevos tests de colisión de nombre en disco pasan para los 3
      endpoints
- [ ] Probado a mano: 2 PDFs reales, mismo nombre, distinta cantidad de
      páginas, subidos al batch → el zip resultante tiene ambos conjuntos
      completos
