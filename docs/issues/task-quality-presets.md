---
slug: task-quality-presets
epic: epic-converter
title: "[Story] Presets de calidad/tamaño en conversiones a imagen (evitar PDFs pesados que traben la UI)"
type: user-story
labels: type:user-story, area:converter, P2, gate:definicion-pendiente
milestone: MixTools v1
---
**As a** usuario que convierte PDFs de imágenes pesadas (ej. escaneos de
50MB)
**I want** poder elegir un balance entre tamaño de archivo y calidad
**so that** no termine con resultados tan pesados que hagan lenta la
página donde los subo después.

## Contexto
Inspirado en cómo lo resuelven herramientas como PDF Guru/PDFGadget: **no
exponen DPI ni % de compresión como números técnicos** — ofrecen 2-3
niveles en lenguaje simple (algo como "Estándar" / "Alta calidad" /
"Máxima compresión"), y cada nivel mapea internamente a valores concretos
de DPI + calidad JPEG.

## Confirmado técnicamente
- `pdf_to_jpg()` hoy solo acepta `dpi` (default 150) — llama
  `pix.save(out_path)` sin ningún control de calidad JPEG.
- PyMuPDF sí soporta un parámetro `jpg_quality` en `pix.save()` — el
  cambio es agregar ese argumento, no reescribir la función.

## Por confirmar antes de poder construirlo (Definición pendiente)
- Qué valores concretos de DPI/`jpg_quality` corresponden a cada preset
- Si aplica solo a PDF→JPG, o también tiene sentido para "Comprimir"
  (utilidad ya planificada en #28) — evaluar compartir el mismo patrón de
  presets entre las dos en vez de duplicar diseño

## Fuera de scope (por ahora)
Construcción — este issue es solo la especificación inicial. Se retoma
después de que #28 (que incluye "Comprimir") esté construido.
