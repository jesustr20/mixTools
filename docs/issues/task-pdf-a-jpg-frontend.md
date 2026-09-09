---
slug: task-pdf-a-jpg-frontend
epic: epic-frontend
title: "[Tech-task] UI de PDF→JPG (walking skeleton, frontend)"
type: tech-task
labels: type:tech-task, area:frontend, P0, gate:listo-para-build
milestone: MixTools v1
---
## Goal
Portar del prototipo HTML **solo** la utilidad PDF→JPG a React, conectada
al endpoint real del backend. El resto de las utilidades quedan pendientes
como issues propios, uno por uno.

## Tasks
- [ ] Requiere `task-frontend-scaffold` ya mergeado (Vite+TS+Tailwind base)
- [ ] Componente `Dropzone` (genérico, reusable para las próximas rebanadas)
- [ ] Componente `PdfToJpgPanel` — sube archivo, llama a
      `POST /api/converter/pdf-a-jpg`, muestra resultado o error
- [ ] `src/lib/api.ts` — función `pdfToJpg(file, dpi)` tipada, nada de
      fetch suelto dentro del componente
- [ ] Probado a mano contra el backend real corriendo en `localhost:8000`
      con un PDF real

## Acceptance
- [ ] Subís un PDF de verdad en el navegador y descargás el JPG (o el ZIP
      si tiene varias páginas) sin usar el prototipo HTML viejo
- [ ] Si el backend no responde, se ve un error legible, no una pantalla
      rota

## Fuera de scope
Las otras utilidades, el rail lateral completo con las 3 herramientas, y
cualquier ajuste visual que no sea indispensable para que esto funcione —
esos vienen en su propio issue.
