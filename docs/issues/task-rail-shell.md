---
slug: task-rail-shell
epic: epic-frontend
title: "[Tech-task] Rail lateral + navegación por chips (shell de la app)"
type: tech-task
labels: type:tech-task, area:frontend, P0, gate:listo-para-build
milestone: MixTools v1
---
## Goal
Migrar la estructura de navegación del prototipo (`frontend-preview/index.html`)
a React: rail lateral con las 3 Herramientas (Conversor, Word→HTML,
Comparador), y dentro de cada una, chips para elegir la utilidad activa.
El panel de PDF→JPG que ya existe se integra ADENTRO de este shell, sin
perder ninguna funcionalidad ya probada.

## Tasks
- [ ] Componente `Rail.tsx` — lista de las 3 Herramientas, estado de cuál
      está activa, estilo fiel al prototipo (fondo oscuro, tal como
      `docs/design-tokens.md` lo define)
- [ ] Componente `Chips.tsx` — fila de utilidades de la Herramienta activa,
      reusable entre las 3 Herramientas
- [ ] `App.tsx` pasa a orquestar: Rail (izquierda) + panel activo (derecha)
      según Herramienta + utilidad seleccionada
- [ ] El panel actual de PDF→JPG (single+batch) se cuelga como la primera
      utilidad de "Conversor" — no se reescribe su lógica, solo se mueve a
      vivir dentro del nuevo shell
- [ ] Word→HTML y Comparador pueden mostrarse como chips "próximamente"
      (deshabilitados) por ahora — sus pantallas reales van en issues
      aparte, esto es solo la estructura de navegación

## Acceptance
- [ ] Al abrir la app, se ve el rail con las 3 Herramientas
- [ ] Conversor está seleccionado por defecto, con PDF→JPG como su chip
      activo, y sigue funcionando exactamente igual que antes (subir 1 o
      varios PDFs, descargar resultado)
- [ ] Cambiar de chip a otra utilidad del Conversor (aunque todavía no
      esté implementada) no rompe nada — puede mostrar un placeholder
- [ ] `npm run lint`, `npm run test`, `npm run build` pasan

## Fuera de scope
Las pantallas reales de las otras utilidades del Conversor (van en
`task-generic-conversion-panel`) y de Word→HTML/Comparador (issues
propios, más adelante).
