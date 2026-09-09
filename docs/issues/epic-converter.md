---
slug: epic-converter
title: "[Epic] Conversor de archivos"
type: epic
labels: type:epic, area:converter, P1, gate:listo-para-build
milestone: MixTools v1
---
## Capacidad de negocio
Reemplazar iLovePDF: convertir, unir, dividir y comprimir PDF/Word/Excel/imágenes
sin límites de suscripción, corriendo en infraestructura propia.

## In scope
- PDF ↔ JPG, JPG → PDF
- Word/Excel/PowerPoint → PDF (LibreOffice headless)
- PDF → Word editable
- Unir, dividir, comprimir PDF

## Out of scope (por ahora)
- OCR de PDFs escaneados
- Watermarks / firmas digitales

## Status
Build inicial completo y probado end-to-end (9 endpoints, ver
`backend/app/tools/converter/`). Pendiente: ajustes módulo por módulo según
Crítica de UI y casos reales.
