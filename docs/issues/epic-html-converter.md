---
slug: epic-html-converter
title: "[Epic] Word a HTML limpio"
type: epic
labels: type:epic, area:html-converter, P1
milestone: MixTools v1
---
## Capacidad de negocio
Reemplazar word2cleanhtml.com: convertir .docx a HTML semántico y limpio,
listo para pegar en Sperant/Liquid, sin la basura mso-* que deja Word.

## In scope
- Conversión docx -> HTML vía mammoth + limpieza con BeautifulSoup
- Quitar mso-*, &nbsp;, spans vacíos, comentarios

## Out of scope (por ahora)
- Insertar bloques Liquid automáticamente (eso es el módulo de merge
  inteligente, más adelante)

## Status
Build inicial funcional y probado con documento sintético. **Pendiente
validar contra las convenciones reales del flujo de Jesús** (font Candara
10pt, colgroup con anchos desde XML, sin invención de estilos) — ver
tech-task asociado.
