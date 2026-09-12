---
slug: task-html-converter-staged-endpoints
epic: epic-html-converter
title: "[Tech-task] Exponer las 3 etapas como endpoints separados (para revelado progresivo en el frontend)"
type: tech-task
labels: type:tech-task, area:html-converter, P0, gate:listo-para-build
milestone: MixTools v1
---
## Goal
Hoy `/convertir` corre las 3 etapas de punta a punta y devuelve un solo
resultado al final — el usuario espera a ciegas 1-3+ minutos sin ver nada
intermedio. La idea nueva: el frontend llama a cada etapa por separado,
encadenadas automáticamente en el código (sin que el usuario apriete un
botón por etapa), mostrando cada resultado apenas llega — así el Proceso 1
(sin IA, rápido) se ve casi al instante, y los siguientes se ven a medida
que van terminando.

## Endpoints nuevos
- `POST /api/html-converter/etapa1` — recibe el `.docx`, devuelve el HTML
  de `docx_to_html()` (Etapa 1, sin IA)
- `POST /api/html-converter/etapa2` — recibe HTML (el de la Etapa 1) como
  JSON `{"html": "..."}` en el body, devuelve el resultado de
  `enhance_tables_with_ai()`
- `POST /api/html-converter/etapa3` — recibe HTML (el de la Etapa 2) como
  JSON `{"html": "..."}` en el body, devuelve el resultado de
  `apply_skeleton_and_verify()`

## Tasks
- [ ] Los 3 endpoints nuevos, reusando las funciones ya existentes en
      `structure.py`/`ai_enhance.py` — no reescribir lógica, solo exponerla
- [ ] Etapa 1 recibe el archivo (multipart, como hoy); Etapa 2 y 3 reciben
      texto plano vía JSON, no un archivo — solo necesitan el HTML de la
      etapa anterior, no el .docx original
- [ ] Devolver JSON (`{"html": "..."}`) en los 3 — el frontend necesita el
      texto para mostrarlo como código, no un archivo descargable
- [ ] Mantener `/convertir` tal cual está (no romper nada existente)
- [ ] Tests de los 3 endpoints nuevos (mockeando DeepSeek para Etapa 2/3,
      igual que ya se hace)

## Acceptance
- [ ] `uv run pytest` completo sigue pasando
- [ ] Probado a mano con `curl`: los 3 endpoints encadenados manualmente
      (pasar el resultado de uno como input del siguiente) dan el mismo
      resultado final que `/convertir` ya da hoy

## Fuera de scope
- Frontend (issue aparte)
- Etapa 4 (Liquid) — no existe todavía, no hay endpoint que exponer
- Streaming/SSE — se evaluó y se descartó por complejidad innecesaria a
  esta escala; 3 endpoints simples encadenados en el frontend alcanzan
