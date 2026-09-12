---
slug: task-fix-stage2-doctype-hallucination
epic: epic-html-converter
title: "[Bug] Etapa 2 a veces envuelve el HTML en DOCTYPE/html/head/body (copia el ejemplo del prompt como si fuera contenido real)"
type: tech-task
labels: type:tech-task, area:html-converter, P0, gate:listo-para-build
milestone: MixTools v1
---
## Bug encontrado
En una prueba real (no mock) contra la API de DeepSeek, `enhance_tables_with_ai`
(Etapa 2, ya mergeada en #43) envolvió el HTML completo en
`<!DOCTYPE html><html><head><style>...</style></head><body>...`, con valores
del bloque de ejemplo del prompt (`font-family: Candara`, márgenes de
`2.5cm`/`3cm`) que **no vienen del documento real** — es contenido
ilustrativo del prompt (explica "así se ve un documento típico"), y el
modelo lo copió como si fuera algo a agregar de verdad.

No pasó en la primera prueba manual (antes del fix de #43 que sacó
`ajusTabla`) — los modelos no son determinísticos, la misma entrada puede
dar resultados distintos entre llamadas. La Etapa 3 (fidelidad) sí detectó
la alteración y degradó correctamente — el bug está contenido, pero hay
que arreglarlo en origen para no depender solo de la red de seguridad de
la Etapa 3.

## Fix
Reforzar el prompt de `enhance_tables_with_ai` con una prohibición
explícita: no agregar `<!DOCTYPE>`, `<html>`, `<head>`, `<body>`, ni copiar
el bloque `<style>` de ejemplo del prompt como contenido de salida — el
ejemplo es solo referencia de convenciones, nunca texto literal a incluir.
La salida debe ser únicamente los tags de contenido (`<p>`, `<table>`,
etc.), sin ningún wrapper de documento completo — igual que llega desde
la Etapa 1.

## Tasks
- [ ] Agregar instrucción explícita y clara en el prompt: "NUNCA agregues
      DOCTYPE, html, head, ni body — tu salida debe ser solo los tags de
      contenido, sin envoltorio de documento"
- [ ] Test: mockear una respuesta que SÍ tenga DOCTYPE/html/head/body
      (simulando este bug real) → confirmar que la verificación de
      fidelidad de texto lo detecta y descarta correctamente (esto ya
      debería funcionar por la Etapa 3, pero conviene un test directo en
      Etapa 2 también, ya que el output "sucio" de Etapa 2 es lo que
      llegaría a producción si algún día se usa sin Etapa 3 después)
- [ ] Probado a mano con la clave real: correr el mismo documento varias
      veces (3-5 llamadas) para aumentar la chance de detectar si el
      comportamiento se repite, y confirmar que ya no aparece el wrapper

## Acceptance
- [ ] `uv run pytest` completo sigue pasando
- [ ] Al menos 3 corridas reales seguidas sin el wrapper de documento
      completo apareciendo
