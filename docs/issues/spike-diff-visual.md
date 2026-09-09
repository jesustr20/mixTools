---
slug: spike-diff-visual
epic: epic-comparator
title: "[Spike/ADR] Diff de texto vs. diff visual en el Comparador"
type: spike
labels: type:spike, area:comparator, P2
milestone: MixTools v1
---
## Decisión a tomar
¿El comparador se queda en diff de texto (v1, ya funciona) o necesita diff
visual real (superposición de páginas como imágenes, detecta cambios de
posición/layout que el texto no ve)?

## Por qué es cara de deshacer
Cambiar de texto a visual no es extender el módulo actual — es prácticamente
reescribirlo (alineación de páginas, comparación de imágenes/contornos en vez
de `difflib`).

## Cómo decidir
Probar el diff de texto actual contra 2-3 pares de documentos reales de
Jesús (ej. dos versiones de un cuadro de acabados). Si el texto alcanza para
detectar lo que importa, se cierra el spike con "texto es suficiente para v1".
Si se pierden cambios posicionales relevantes, se abre como epic aparte.

## Status
Pendiente — bloqueado por tener documentos reales para probar.
