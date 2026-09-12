---
slug: task-html-converter-multi-format
epic: epic-html-converter
title: "[Story] Aceptar PDF y Excel como entrada además de Word (clientes mandan distintos formatos)"
type: user-story
labels: type:user-story, area:html-converter, P2, gate:definicion-pendiente
milestone: MixTools v1
---
**As a** usuario que recibe documentos de clientes en formatos variados
**I want** poder subir PDF o Excel además de Word
**so that** no tenga que convertir manualmente antes de usar la herramienta.

## Contexto
Los clientes mandan indistintamente `.doc`, `.docx`, PDF, o Excel con
tablas/cuadros. La Etapa 1 (#40) solo lee `.docx` — esto es correcto como
punto de partida (walking skeleton), pero deja 3 casos sin cubrir.

## Por formato

- **`.doc`** — el más simple: convertir a `.docx` con LibreOffice
  (`soffice --headless --convert-to docx`) antes de pasarlo por la Etapa 1
  existente. No necesita un extractor nuevo.
- **PDF** — el más difícil. No tiene la estructura XML que sí tiene
  `.docx` (`w:shd`, `tblGrid`, `gridSpan`) — es un formato de renderizado
  de página, no de documento estructurado. Necesita su propio extractor,
  probablemente usando detección de tablas de PyMuPDF
  (`page.find_tables()`), ya dependencia del proyecto. Desarrollo aparte,
  no reusa la Etapa 1 tal cual.
- **Excel** — más parecido en espíritu al `.docx` (tiene su propio XML con
  fusión de celdas y colores), se leería con `openpyxl` (ya dependencia)
  con una lógica de extracción similar a la Etapa 1, pero es código
  distinto, no el mismo módulo.

## Fuera de scope (por ahora)
Se retoma después de que el camino completo de `.docx` (3 etapas + Liquid)
esté funcionando de punta a punta y probado. No bloquea el trabajo en
curso.
