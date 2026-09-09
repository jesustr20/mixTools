---
slug: epic-frontend
title: "[Epic] Interfaz (UI/UX)"
type: epic
labels: type:epic, area:frontend, P1
milestone: MixTools v1
---
## Capacidad de negocio
Una interfaz "mesa de trabajo" — no dashboard SaaS genérico — donde cada
Herramienta (Conversor, Word→HTML, Comparador) se navega con sus utilidades
como pestañas/chips, lo suficientemente pulida como para que alguien más
quiera usarla.

## In scope
- Prototipo interactivo HTML (dirección visual: mesa de dibujo/plano técnico)
- Traducción del prototipo aprobado a React + Tailwind

## Out of scope
- Autenticación / multi-usuario (es una herramienta personal por ahora)

## Status
Prototipo HTML entregado (`frontend-preview/index.html`), sirvió para
validar la dirección visual (mesa de dibujo/plano técnico) y quedó
aprobado en la práctica durante la conversación. **Migración a React
avanza módulo por módulo**, junto con el backend — no se porta todo de una.
Ver `task-frontend-scaffold` (base técnica, una sola vez) y
`task-pdf-a-jpg-frontend` (primera rebanada real).
