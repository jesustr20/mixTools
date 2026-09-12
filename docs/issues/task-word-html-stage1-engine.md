---
slug: task-word-html-stage1-engine
epic: epic-html-converter
title: "[Tech-task] Etapa 1 — motor determinístico con extracción real del XML del .docx"
type: tech-task
labels: type:tech-task, area:html-converter, P0, gate:listo-para-build
milestone: MixTools v1
---
## Goal
El motor actual (`word_to_clean_html`, mammoth + BeautifulSoup) no extrae
colores de tema resueltos, anchos de columna reales, ni colspan/rowspan
desde el XML del `.docx` — solo el HTML genérico que da mammoth. Esta
etapa reemplaza/complementa esa extracción con lectura directa del XML
(via `python-docx`, ya es dependencia del proyecto), sin usar IA todavía
(eso es la Etapa 2, issue aparte).

## Referencia
Issue #7 tiene la arquitectura completa de 3 etapas — esta tarea es
específicamente la Etapa 1.

## Tasks
- [ ] Nueva función (o extender la existente) que recorra el `.docx` con
      `python-docx`, en orden real del documento (no colapsar estructura)
- [ ] Resolver `w:shd fill` (color de fondo de celda) incluyendo colores de
      tema con cálculo de tint (HSL), no solo colores directos
- [ ] Extraer anchos de columna reales desde `tblGrid` (en twips,
      convertidos a porcentaje)
- [ ] Extraer `gridSpan` (colspan) y `vMerge` (rowspan) reales
- [ ] Detectar el patrón de "columnas simuladas con tabs" (una celda con
      `\t` separando lo que visualmente son 2 columnas) y reconstruirlo
      como una fila de 2 columnas reales
- [ ] Cero `&nbsp;` en la salida — espacio real o celda vacía
- [ ] `font-family`/`font-size` tomados del documento real, no
      hardcodeados

## Acceptance
- [ ] Test con un `.docx` real que tenga: una tabla con celdas de color de
      tema, una celda con colspan, una celda con rowspan → confirmar que
      el HTML de salida tiene los valores exactos (no aproximados)
- [ ] Test con un `.docx` que tenga el patrón de tabs-como-columnas →
      confirmar que se reconstruye como tabla real
- [ ] `uv run pytest` completo sigue pasando

## Fuera de scope
- Cualquier llamada a IA/DeepSeek (Etapa 2, issue aparte)
- El esqueleto de salida fijo (`.cabecera`/`.pie_pagina`/etc.) — esta etapa
  solo convierte el contenido, no arma el envoltorio completo todavía
- Los bloques de Liquid — vienen después de que las 3 etapas base
  funcionen
