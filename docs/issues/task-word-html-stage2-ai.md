---
slug: task-word-html-stage2-ai
epic: epic-html-converter
title: "[Tech-task] Etapa 2 — IA quirúrgica con DeepSeek (corrige tablas complejas)"
type: tech-task
labels: type:tech-task, area:html-converter, P0, gate:listo-para-build
milestone: MixTools v1
---
## Goal
La Etapa 1 (#40, ya mergeada) extrae la estructura real del `.docx` — pero
hay casos que un motor determinístico no puede resolver bien: tablas con
patrones de fusión complejos, secciones donde el layout visual del PDF/Word
no se deduce solo de gridSpan/vMerge. Esta etapa le pasa el HTML de la
Etapa 1 a DeepSeek con un prompt de tablas, para que corrija **solo lo
puntual** — no reescribe el documento entero.

## Confirmado
- `DEEPSEEK_API_KEY` ya configurada como variable de entorno (mismo patrón
  que `AUTH_USER`/`AUTH_PASSWORD`)
- La API de DeepSeek es compatible con el formato de OpenAI — un POST con
  `httpx` alcanza, no hace falta SDK
- `httpx` ya es dependencia del proyecto (hoy solo en el grupo `dev` — hay
  que moverla a dependencias principales, la va a usar código de
  producción, no solo los tests)

## Tasks
- [ ] Mover `httpx` de `[dependency-groups].dev` a `[project].dependencies`
      en `pyproject.toml`
- [ ] Función `enhance_tables_with_ai(html: str) -> str` que llama a la API
      de DeepSeek (`https://api.deepseek.com/chat/completions` o el
      endpoint real que confirme la documentación oficial — no asumir la
      URL sin verificarla) con el HTML de la Etapa 1 + el prompt de tablas
      (ver contexto abajo)
- [ ] Manejo de error explícito: si `DEEPSEEK_API_KEY` no está seteada, o
      la llamada falla (timeout, error de API), la función debe devolver
      el HTML de la Etapa 1 **sin modificar** (degradar con gracia, nunca
      romper la conversión completa por un fallo de IA)
- [ ] Test: mockear la llamada HTTP a DeepSeek (no gastar tokens reales en
      cada corrida de tests) y confirmar que el HTML devuelto por la
      función es el que vino de la respuesta mockeada
- [ ] Test: simular que `DEEPSEEK_API_KEY` no existe → confirmar que
      devuelve el HTML original sin llamar a ninguna API

## Contexto — prompt de tablas
Existe un prompt largo (de trabajo real de Jesús) explicando cómo resolver
colspan/rowspan complejos y matching de colores exactos del documento
original, con la regla explícita "no imaginar, no alucinar colores que no
estén en el original". Se pide en el prompt de construcción de DeepSeek
para esta tarea — no se documenta acá completo porque es largo.

## Acceptance
- [ ] `uv run pytest` completo sigue pasando (incluye los mocks nuevos, sin
      gastar tokens reales de DeepSeek en CI)
- [ ] Probado a mano una sola vez con la clave real: convertir un `.docx`
      con una tabla compleja de verdad → confirmar que el resultado
      mejora respecto a la Etapa 1 sola

## Fuera de scope
- El esqueleto de salida fijo y la pasada de fidelidad final (Etapa 3,
  issue aparte)
- Bloques de Liquid
- Cualquier UI — esto es solo backend
