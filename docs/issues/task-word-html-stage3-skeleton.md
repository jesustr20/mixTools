---
slug: task-word-html-stage3-skeleton
epic: epic-html-converter
title: "[Tech-task] Etapa 3 — esqueleto fijo + pasada de fidelidad final (IA, DeepSeek)"
type: tech-task
labels: type:tech-task, area:html-converter, P0, gate:listo-para-build
milestone: MixTools v1
---
## Goal
Tercera y última pasada de IA antes de Liquid (issue aparte, #4). Toma el
HTML ya corregido de la Etapa 2 y:
1. Lo envuelve en el esqueleto de salida fijo (`.cabecera`/`.pie_pagina`/
   `.espacio-cabecera`/`.espacio-pie`/`.cuerpo-texto`/`.firmas`, estructura
   `<thead>`/`<tfoot>`/`<tbody>`)
2. Revisa fidelidad general contra el documento original — que nada se
   haya perdido o distorsionado en las etapas anteriores
3. Tiene libertad de crear clases CSS nuevas si hace falta para que la
   estructura no quede "engorrosa" — no está atada 100% al set de clases
   ya visto, puede resolver con criterio

## Confirmado (de #7 y conversación con Jesús)
- **Regla de fidelidad textual (crítica)**: el texto fijo (todo lo que NO
  se convierte a Liquid) debe quedar **exactamente igual, carácter por
  carácter**, al original — solo puede cambiar la estructura HTML
  (etiquetas, clases, envoltorios), nunca el contenido textual en sí. Esto
  habilita que el futuro módulo Comparador (epic-comparator) pueda
  comparar el resultado final contra el original sin falsos positivos por
  texto "mejorado" por la IA. Esta regla aplica también retroactivamente
  como principio para la Etapa 2 (ya mergeada) — no se reabre ese PR, pero
  queda documentado como criterio para cualquier ajuste futuro.
- Sin Liquid todavía — eso es la Etapa 4, separada a propósito (más fácil
  debuggear cada pieza sola: si algo sale mal, se sabe si fue el esqueleto
  o fue Liquid)
- Para el usuario final, las etapas corren encadenadas automáticamente en
  una sola conversión — la separación es solo interna/de código

## Tasks
- [ ] Función `apply_skeleton_and_verify(html: str) -> str` (o nombre que
      el agente prefiera, consistente con `ai_enhance.py`) — llama a
      DeepSeek con un prompt que incluya el ejemplo de esqueleto ya
      confirmado como bueno (Ficha de Actualización de Datos / Convenio de
      Separación — ver conversación en #7) más la libertad de crear clases
      propias si hace falta
- [ ] Mismo patrón de degradación con gracia que la Etapa 2: si
      `DEEPSEEK_API_KEY` falta o la llamada falla, devolver el HTML de la
      Etapa 2 sin el esqueleto (no romper la conversión completa)
- [ ] Wiring: encadenar las 3 etapas en una sola función de conveniencia
      (ej. `word_to_html_full_pipeline(docx_path) -> str`) que llama
      Etapa 1 → Etapa 2 → Etapa 3 en orden
- [ ] Tests con mocks (igual que Etapa 2) — no gastar tokens reales en CI
- [ ] Retirar `word_to_clean_html` (el motor viejo de mammoth) SOLO si el
      pipeline nuevo completo ya se verificó a mano que funciona bien de
      punta a punta — si hay dudas, dejarlo y anotarlo como pendiente, no
      borrar a ciegas

## Acceptance
- [ ] `uv run pytest` completo sigue pasando (mocks, cero costo de API)
- [ ] Probado a mano con la clave real: `.docx` completo → pipeline de 3
      etapas → HTML final tiene el esqueleto correcto y sigue siendo fiel
      al original (comparar visualmente)

## Fuera de scope
- Liquid (Etapa 4, issue aparte)
- Multi-formato (PDF/Excel, #44)
