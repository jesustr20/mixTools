---
slug: task-generic-conversion-panel
epic: epic-frontend
title: "[Tech-task] Componente genérico de conversión + 5 utilidades simples del Conversor"
type: tech-task
labels: type:tech-task, area:frontend, P0, gate:listo-para-build
milestone: MixTools v1
---
## Goal
La mayoría de las utilidades del Conversor comparten el mismo contrato:
subís uno o varios archivos de un tipo, se convierten, bajás el resultado
con el mismo sello "LISTO". En vez de 5 pantallas casi idénticas, un solo
componente configurable que sirve para todas.

## Utilidades a conectar (todas con este mismo patrón)
- JPG→PDF (`POST /api/converter/jpg-a-pdf`, varios archivos)
- Office→PDF (`POST /api/converter/office-a-pdf`, 1 archivo)
- PDF→Word (`POST /api/converter/pdf-a-word`, 1 archivo)
- Dividir PDF (`POST /api/converter/split`, 1 archivo)
- Comprimir PDF (`POST /api/converter/comprimir`, 1 archivo)

## Tasks
- [ ] Componente `GenericConversionPanel.tsx` que reciba por props: label,
      endpoint, extensión(es) aceptada(s), si acepta 1 o varios archivos,
      nombre sugerido del archivo de salida
- [ ] `src/lib/api.ts` — una función genérica `convertFile(endpoint, files)`
      que reemplace tener que escribir una función nueva por cada endpoint
      (reusa el patrón de XHR con progreso real de `task-real-upload-progress`
      si ya está mergeado; si no, usar el mismo patrón que ya tienen
      `pdfToJpg`/`batchPdfsToJpg`)
- [ ] Conectar las 5 utilidades de la lista de arriba usando este
      componente, como chips nuevos dentro de "Conversor"

## Acceptance
- [ ] Las 5 utilidades funcionan de verdad contra el backend real (probado
      a mano con archivos reales, no solo con el ojo)
- [ ] Ningún archivo de componente nuevo por utilidad — todas usan
      `GenericConversionPanel`
- [ ] `npm run lint`, `npm run test`, `npm run build` pasan

## Fuera de scope
"Unir PDFs" (patrón distinto, issue aparte) y las utilidades de las otras
2 Herramientas.
