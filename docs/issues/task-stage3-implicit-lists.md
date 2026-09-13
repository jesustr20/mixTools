---
slug: task-stage3-implicit-lists
epic: epic-html-converter
title: "[Story] Etapa 3: reconocer listas SIN marcador escrito (párrafos paralelos terminados en punto y coma)"
type: user-story
labels: type:user-story, area:html-converter, P1, gate:listo-para-build
milestone: MixTools v1
---
## Contexto
Confirmado en pruebas reales (#69/#71): el prompt actual solo convierte en
`<ol>`/`<li>` los párrafos que YA tienen un marcador literal escrito
((i), 1., etc.) — con el marcador conservado como texto, correctamente.

Pero hay un patrón distinto, muy común en documentos legales, que el
prompt actual no cubre: varios párrafos cortos y paralelos, cada uno
terminando en punto y coma (menos el último, que cierra en punto), SIN
ningún número o letra escrito — un patrón de lista implícita, reconocible
por su forma, no por un carácter de marcador.

Confirmado en un ejemplo real: la Cláusula Octava del Convenio de
Separación (6 párrafos tipo "La realización de gestiones...;", "La
entrega de los documentos...;", etc.) es exactamente este caso — Claude
(con más libertad) sí lo reconoció y armó una lista; DeepSeek con el
prompt actual no, porque nunca le dimos ese permiso.

## Por qué es seguro (no rompe fidelidad)
Como no hay ningún marcador literal en el texto original, envolver estos
párrafos en `<ol>` con numeración generada por CSS (o simplemente `<ul>`
con viñetas) **no borra ningún carácter** — no hay nada que perder. Es
justo el caso opuesto al de los marcadores explícitos: ahí SÍ había que
preservar el texto; acá no hay texto de marcador que preservar, así que
la numeración/viñeta generada por CSS es segura.

## Regla nueva a agregar (además de la que ya existe, no reemplazarla)
Además de los párrafos que YA tienen marcador, reconocer también: 2 o más
párrafos consecutivos que se leen como una serie paralela — normalmente
porque cada uno (menos el último) termina en punto y coma, siguiendo una
oración introductoria que termina en dos puntos (":") — y agruparlos en
una lista (`<ol>` con numeración CSS, o `<ul>` con viñetas — a elección
según se vea mejor), sin necesidad de marcador literal porque no hay
ninguno que conservar.

## Tasks
- [ ] Agregar esta regla a `_SKELETON_PROMPT`, aclarando explícitamente
      que es DISTINTA de la regla de marcador literal — acá SÍ se permite
      numeración/viñetas generadas por CSS, precisamente porque no hay
      texto de marcador que perder
- [ ] Test: mockear una respuesta que agrupe párrafos sin marcador en una
      lista con numeración CSS → debe ACEPTARSE por la verificación de
      fidelidad (a diferencia del caso de #69, donde quitar un marcador
      SÍ existente se rechaza)
- [ ] Probado a mano con el documento real: la Cláusula Octava (y
      cualquier otra similar) debería salir como lista

## Acceptance
- [ ] `uv run pytest` completo sigue pasando
- [ ] Confirmado a mano: Cláusula Octava del Convenio de Separación sale
      como lista real, sin perder ningún carácter (no había marcador que
      perder)
