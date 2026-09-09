---
slug: story-html-conventions
epic: epic-html-converter
title: "[Story] Word->HTML respeta las convenciones reales de conversión"
type: user-story
labels: type:user-story, area:html-converter, P1, gate:critica-pendiente
milestone: MixTools v1
---
**As a** usuario que convierte documentos de proyectos inmobiliarios a HTML
**I want** que el HTML de salida respete mis convenciones ya establecidas
**so that** no tenga que corregirlo a mano antes de subirlo a Sperant.

## Acceptance
- [ ] `font-family: Candara`, `font-size: 10pt` aplicado igual que en las
      conversiones manuales
- [ ] Cero `&nbsp;` en la salida (espacio real o celda vacía, nunca la entidad)
- [ ] Tablas con `border-collapse: collapse`, `cellpadding="0"`, `cellspacing="0"`
- [ ] `colgroup` con anchos de columna calculados desde el XML/twips real del
      .docx, no inventados
- [ ] Ningún color/estilo que no exista en el `.docx` fuente

## Notas
Esto requiere leer `w:shd fill` y medidas reales del XML del docx, no solo el
HTML que produce mammoth por defecto — mammoth no expone eso directamente,
hay que complementarlo leyendo el .docx como zip/XML aparte.
