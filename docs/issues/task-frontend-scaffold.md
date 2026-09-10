---
slug: task-frontend-scaffold
epic: epic-frontend
title: "[Tech-task] Scaffold de React + TypeScript + Vite + Tailwind"
type: tech-task
labels: type:tech-task, area:frontend, P0, gate:listo-para-build
milestone: MixTools v1
---
## Goal
Base técnica del frontend definitivo (ADR-0001) — esto es tooling/build,
no diseño.

## Tasks
- [ ] `npm create vite@latest frontend -- --template react-ts`
- [ ] Tailwind instalado y configurado (`tailwind.config.js`,
      `postcss.config.js`)
- [ ] Vitest + React Testing Library configurados, con un test de humo
- [ ] Estructura de carpetas: `src/components/`, `src/lib/api.ts` (fetch
      helpers hacia los mismos endpoints ya probados del backend)
- [ ] `.env.example` con `VITE_API_BASE=http://localhost:8000`

## Fuera de scope (todavía)
Portar los componentes reales del prototipo (`Rail`, `Chips`, `Dropzone`,
`Result`) — eso avanza módulo por módulo, empezando por
`task-pdf-a-jpg-frontend`.
