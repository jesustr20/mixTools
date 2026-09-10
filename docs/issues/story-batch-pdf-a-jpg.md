---
slug: story-batch-pdf-a-jpg
epic: epic-converter
title: "[Story] Subir varios PDFs a la vez y descargar todo organizado en un .zip"
type: user-story
labels: type:user-story, area:converter, P1, gate:critica-pendiente
milestone: MixTools v1
---
**As a** usuario que digitaliza varios documentos de una vez (ej. varios
comprobantes escaneados como PDF)
**I want** subir varios PDFs juntos y que cada uno se convierta a JPG,
organizados y comprimidos en un solo archivo
**so that** no tenga que convertir y descargar uno por uno.

## Comportamiento exacto

- Si se sube **un solo PDF de 1 página** → se descarga la imagen JPG
  directa, sin zip (comportamiento actual, sin cambios).
- Si se suben **2 o más PDFs**:
  - Por cada PDF con **1 página**: la imagen queda suelta dentro del zip,
    nombrada como el PDF de origen (ej. `recibo1.jpg`).
  - Por cada PDF con **2 o más páginas**: se crea una carpeta con el nombre
    del PDF de origen, y adentro las imágenes de cada página
    (ej. `recibo2/pagina_1.jpg`, `recibo2/pagina_2.jpg`, ...).
  - Todo (carpetas sueltas + imágenes sueltas) se comprime en un único
    `.zip` llamado `conversion_mixtools.zip`.

## Acceptance

- [ ] Subir 1 PDF de 1 página → sigue bajando como `.jpg` directo (no rompe
      el comportamiento ya validado en #12)
- [ ] Subir 2 PDFs de 1 página cada uno → `conversion_mixtools.zip` con 2
      `.jpg` sueltos, nombrados por su PDF de origen
- [ ] Subir 2 PDFs, uno de 1 página y otro de 3 páginas →
      `conversion_mixtools.zip` con 1 `.jpg` suelto + 1 carpeta con 3 `.jpg`
      adentro
- [ ] Subir 3+ PDFs mixtos → misma lógica, sin importar la combinación

## Notas técnicas
- El patrón de aceptar `files: list[UploadFile]` ya existe en `merge` y
  `jpg-a-pdf` — se puede seguir el mismo.
- Es un endpoint/flujo nuevo, no se modifica el `POST /api/converter/pdf-a-jpg`
  ya construido y mergeado en #12/#15 — ese sigue existiendo tal cual para
  un solo PDF.
