---
slug: task-fix-stage3-wrapper
epic: epic-html-converter
title: "[Bug] Etapa 3 agrega DOCTYPE/html/head/body — debe ser fragmento puro (mismo bug que #47, pero en Etapa 3)"
type: tech-task
labels: type:tech-task, area:html-converter, P0, gate:listo-para-build
milestone: MixTools v1
---
## Bug encontrado y confirmado
La plantilla real (`_SKELETON_TEMPLATE` en `ai_enhance.py`) nunca incluye
`<!DOCTYPE html><html><head>...<body>...</body></html>` — arranca directo
con `<style>` y sigue con `<div class="cabecera">`. Es un FRAGMENTO,
pensado para pegar dentro de un sistema existente (Sperant), no una página
independiente.

Confirmado en producción (documento real, "Convenio de Separación"): la
Etapa 3 agregó ese wrapper de todas formas, sin que se lo pidiéramos.

## Por qué no lo cachó la verificación de fidelidad existente
`_normalize_visible_text()` (la función que compara el texto antes/después
para detectar alteraciones) **quita todas las etiquetas HTML** antes de
comparar — así que agregar `<!DOCTYPE>`/`<html>`/`<head>`/`<body>` alrededor
del contenido no cambia el texto visible extraído, y el chequeo de
fidelidad pasa sin detectar el problema. Es un punto ciego real: la
verificación de fidelidad protege el TEXTO, no la ESTRUCTURA.

## Fix (mismo patrón que #47/#48, aplicado a Etapa 3)
1. Reforzar `_SKELETON_PROMPT` con una instrucción explícita: nunca
   agregar DOCTYPE/html/head/body, la salida debe empezar directo con
   `<style>` tal como la plantilla de referencia
2. Reusar (o extender) `_has_document_wrapper()` — ya existe, se usa en
   `enhance_tables_with_ai` — aplicarla también en
   `apply_skeleton_and_verify`: si la salida del modelo tiene el wrapper,
   tratarlo igual que una falla de fidelidad (descartar, devolver el HTML
   de entrada sin el esqueleto, loguear)

## Tasks
- [ ] Agregar la instrucción al prompt
- [ ] Aplicar `_has_document_wrapper()` (o equivalente) también en
      `apply_skeleton_and_verify`, antes o junto con la verificación de
      fidelidad textual
- [ ] Test: mockear una respuesta CON el wrapper de documento completo →
      confirmar que se rechaza y degrada, igual que el test ya existente
      para la Etapa 2

## Acceptance
- [ ] `uv run pytest` completo sigue pasando
- [ ] Probado a mano (si hay clave disponible): confirmar que la salida
      real ya no tiene DOCTYPE/html/head/body, arranca directo con
      `<style>`
