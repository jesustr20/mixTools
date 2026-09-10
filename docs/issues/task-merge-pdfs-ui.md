---
slug: task-merge-pdfs-ui
epic: epic-frontend
title: "[Tech-task] UI de Unir PDFs (con orden de archivos)"
type: tech-task
labels: type:tech-task, area:frontend, P1, gate:listo-para-build
milestone: MixTools v1
---
## Goal
"Unir PDFs" no encaja en el componente genérico porque el ORDEN de los
archivos importa (define el orden final de páginas en el PDF unido) — el
usuario necesita poder reordenarlos antes de convertir, no solo listarlos.

## Tasks
- [ ] Panel de "Unir PDFs" con lista de archivos reordenable (arrastrar
      para cambiar el orden, o botones subir/bajar — lo que sea más simple
      de implementar bien)
- [ ] Llama a `POST /api/converter/merge` respetando el orden mostrado en
      pantalla
- [ ] Mismo patrón de resultado (sello "LISTO" + descarga) que el resto

## Acceptance
- [ ] Subir 3+ PDFs, reordenarlos, convertir → el PDF resultante respeta
      el orden que se ve en pantalla, no el orden en que se subieron
- [ ] `npm run lint`, `npm run test`, `npm run build` pasan

## Fuera de scope
Cualquier otra utilidad — este issue es solo "Unir".
