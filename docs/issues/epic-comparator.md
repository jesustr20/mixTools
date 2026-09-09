---
slug: epic-comparator
title: "[Epic] Comparador de documentos"
type: epic
labels: type:epic, area:comparator, P1
milestone: MixTools v1
---
## Capacidad de negocio
Reemplazar Draftable: comparar dos versiones de un documento (PDF, Word o
Excel, en cualquier combinación) y mostrar qué cambió.

## In scope (v1)
- Extracción de texto por tipo de archivo
- Diff a nivel de palabra con resaltado inline (estilo Draftable "inline mode")
- Estadísticas de similitud

## Out of scope (v1, evaluar en Spike)
- Diff visual real (superposición de páginas como imágenes, cambios de
  posición/layout) — ver spike asociado antes de decidir si entra a v1 o v2.

## Status
Build inicial funcional y probado end-to-end. Diff de texto, no visual.
