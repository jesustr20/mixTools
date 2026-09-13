---
slug: task-stage3-list-and-placeholder-formatting
epic: epic-html-converter
title: "[Story] Etapa 3: convertir enumeraciones en listas reales + resaltar blancos [●] (sin romper fidelidad)"
type: user-story
labels: type:user-story, area:html-converter, P1, gate:listo-para-build
milestone: MixTools v1
---
## Contexto
Comparando el resultado actual de la Etapa 3 contra un ejemplo hecho a
mano (con más libertad de reestructuración), se identificaron dos mejoras
reales que la Etapa 3 podría hacer sin romper la regla de fidelidad
textual ya existente:

1. Párrafos que empiezan con `(i)`, `(ii)`, `(iii)` (o `1.`, `2.`, etc.)
   deberían convertirse en `<ol>`/`<li>` reales, no quedar como texto
   plano con el número escrito a mano dentro de un `<p>`
2. Los blancos `[●]` / `[TEXTO ENTRE CORCHETES]` deberían resaltarse
   visualmente, por ejemplo con `<span style="background-color: yellow;">`
   — mismo patrón que usa el propio editor de plantillas de Sperant

## Restricción técnica confirmada (importante, no opcional)
`_normalize_visible_text()` compara texto **literal** de las etiquetas,
no la página renderizada. Si el modelo convierte "(i) Vinculado..." en una
lista con numeración generada por CSS (`<ol>` sin el "(i)" como texto
literal), los caracteres "(i)" desaparecen de lo que la verificación
puede ver, y el chequeo de fidelidad lo rechazaría — aunque visualmente
se vea bien en el navegador. **El fix debe indicarle al modelo que
mantenga el marcador ("(i)", "1.", etc.) como texto literal dentro del
`<li>`**, no delegarlo a un contador CSS — así el texto sigue siendo
idéntico carácter por carácter y la verificación de fidelidad sigue
funcionando sin cambios.

El resaltado amarillo de `[●]` no tiene este problema — envolver en
`<span>` no quita ni agrega caracteres, es seguro tal cual.

## Tasks
- [ ] Ampliar `_SKELETON_PROMPT` con instrucciones explícitas para las dos
      mejoras, incluyendo la restricción de arriba (marcador literal
      dentro del `<li>`, no generado por CSS)
- [ ] Test: mockear una respuesta que SÍ convierta correctamente
      (marcador literal preservado) → debe pasar la verificación de
      fidelidad
- [ ] Test: mockear una respuesta que remueva el marcador literal
      (delegándolo a CSS) → debe seguir siendo rechazada por la
      verificación existente (confirma que la regla de fidelidad sigue
      protegiendo aunque ahora permitamos más libertad estructural)
- [ ] Probado a mano con la clave real: el documento de prueba
      (Convenio de Separación, que tiene varios "(i)"/"(ii)"/"(iii)" en
      la Cláusula Novena) → confirmar que salen como `<ol>`/`<li>` reales
      con el marcador conservado, y que los `[●]` quedan resaltados

## Acceptance
- [ ] `uv run pytest` completo sigue pasando
- [ ] Confirmado a mano: el resultado real tiene listas semánticas +
      resaltado, y sigue pasando la verificación de fidelidad (no
      degrada al HTML sin esqueleto)
