---
slug: task-word-html-frontend
epic: epic-html-converter
title: "[Tech-task] Activar la Herramienta Word→HTML en el frontend (usando GenericConversionPanel)"
type: tech-task
labels: type:tech-task, area:html-converter, P0, gate:listo-para-build
milestone: MixTools v1
---
## Goal
Conectar el backend ya terminado (#40/#42/#45/#49) a una pantalla real en
el frontend, reusando `GenericConversionPanel` (mismo patrón que las
utilidades simples del Conversor) — no hace falta un componente nuevo.

## Confirmado
- `App.tsx` tiene la condición del render de `GenericConversionPanel`
  atada a `activeTool === 'converter'` — hay que generalizarla para que
  cualquier Herramienta con una utilidad `conversion` la use, no solo el
  Conversor
- El endpoint `POST /api/html-converter/convertir` con `devolver_json=false`
  (default) ya devuelve un archivo descargable (`text/html`), mismo patrón
  Blob que usa `GenericConversionPanel` — no hace falta lógica nueva de API

## Tasks
- [ ] En `tools.ts`: cambiar `available: false` → `true` en la Herramienta
      `html`, y agregar una utilidad con `conversion` apuntando a
      `/api/html-converter/convertir`, `accept: '.docx'`, `multiple: false`
- [ ] En `App.tsx`: generalizar la condición del render de
      `GenericConversionPanel` para que no esté atada a
      `activeTool === 'converter'` — cualquier utilidad con `conversion`
      configurada debe poder usarlo, sea de la Herramienta que sea
- [ ] Confirmar que Conversor sigue funcionando exactamente igual después
      del cambio (no romper nada existente)

## Acceptance
- [ ] `npm run lint`, `npm run test`, `npm run build` pasan
- [ ] Probado a mano en el navegador: entrar a "Word → HTML", subir un
      `.docx` real, confirmar que descarga un `.html` con el esqueleto
      completo (si `DEEPSEEK_API_KEY` está configurada en el backend que
      esté corriendo)

## Fuera de scope
- Liquid (issue aparte)
- Cualquier cambio a las utilidades del Conversor
