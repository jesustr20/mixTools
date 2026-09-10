---
slug: task-unify-pdf-to-jpg-view
epic: epic-frontend
title: "[Tech-task] Unificar PDF→JPG en una sola vista (reemplaza el enfoque de 2 pestañas de #18)"
type: tech-task
labels: type:tech-task, area:frontend, P0, gate:listo-para-build
milestone: MixTools v1
---
## Goal
Reemplazar el enfoque de dos pestañas ("Un PDF" / "Varios PDFs", construido
en el PR #18 — cerrado sin mergear) por **una sola vista**: un dropzone que
acepta cualquier cantidad de PDFs, y el frontend decide solo qué endpoint
llamar según cuántos archivos hay. Además, esto arregla de raíz un bug real
que apareció en #18: al soltar PDFs uno por uno (no todos juntos), cada
archivo nuevo pisaba al anterior en vez de acumularse — el estado se
reemplazaba en vez de agregarse.

## Comportamiento exacto

- Un solo dropzone, siempre en modo múltiple.
- Cada archivo que soltás/seleccionás se **agrega** a la lista (nunca la
  reemplaza) — soltar de a uno o todos juntos debe dar el mismo resultado
  final.
- Lista de archivos seleccionados, cada uno con botón de quitar.
- Botón "Convertir" habilitado con 1 o más archivos (no hace falta esperar
  a tener 2+).
- Al convertir:
  - **1 archivo** → llama a `POST /api/converter/pdf-a-jpg` (el endpoint ya
    existente y validado en #12/#15) — resultado: jpg directo (1 página) o
    zip de páginas (2+ páginas).
  - **2+ archivos** → llama a `POST /api/converter/batch-pdf-a-jpg` (ya
    mergeado en #17) — resultado: `conversion_mixtools.zip`.
- El resultado (sello "LISTO" + descarga) se ve igual sin importar qué
  camino se tomó — el usuario no necesita saber que hay dos endpoints
  distintos atrás.

## Tasks
- [ ] Consolidar `PdfToJpgPanel.tsx` y `BatchPdfToJpgPanel.tsx` (de #18, en
      su rama sin mergear) en un solo componente. Se puede reusar código de
      cualquiera de los dos, pero el resultado final es UN componente, no
      dos coexistiendo con un toggle.
- [ ] Arreglar el bug de acumulación en el estado del dropzone (setState
      funcional que agrega al array anterior, no lo reemplaza) — agregar un
      test que reproduzca el bug (soltar 2 archivos por separado, no
      juntos) y confirme que ambos quedan en la lista.
- [ ] `App.tsx` ya no tiene pestañas — un solo panel.
- [ ] `src/lib/api.ts` puede mantener `pdfToJpg` y `batchPdfsToJpg` como dos
      funciones separadas (ya probadas) — el componente decide cuál llamar
      según `files.length`.

## Acceptance
- [ ] Soltar 1 PDF, después otro, después un tercero (uno por vez, no todos
      juntos) → los 3 quedan en la lista, ninguno se pierde
- [ ] Convertir con 1 archivo → mismo resultado que el endpoint single ya
      daba antes
- [ ] Convertir con 2+ → `conversion_mixtools.zip` como en #17
- [ ] No quedan pestañas ni toggles en la UI

## Fuera de scope
El rail lateral con las 3 herramientas — sigue siendo una vista standalone
por ahora.
