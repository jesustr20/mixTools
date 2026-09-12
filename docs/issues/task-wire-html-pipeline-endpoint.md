---
slug: task-wire-html-pipeline-endpoint
epic: epic-html-converter
title: "[Tech-task] Conectar el endpoint /convertir al pipeline nuevo de 3 etapas (retirar mammoth)"
type: tech-task
labels: type:tech-task, area:html-converter, P0, gate:listo-para-build
milestone: MixTools v1
---
## Goal
El endpoint `POST /api/html-converter/convertir` hoy usa el motor viejo
(`engine.word_to_clean_html`, basado en mammoth). Las 3 etapas nuevas
(#40, #42, #45/#46) ya están mergeadas y **verificadas de punta a punta
con documentos reales** — se cumple la condición que dejamos anotada en
#45 para retirar el motor viejo.

## Tasks
- [ ] Cambiar el endpoint para usar
      `ai_enhance.word_to_html_full_pipeline(docx_path)` en vez de
      `engine.word_to_clean_html`
- [ ] Decidir qué hacer con el parámetro `strip_styles` — era específico
      del motor viejo (limpieza de `mso-*`/`font-family` con
      BeautifulSoup). El pipeline nuevo ya maneja esto de otra forma
      (extracción real + IA). Explicar la decisión en el PR: ¿se elimina
      el parámetro, se ignora silenciosamente, o se mapea a algo
      equivalente?
- [ ] Retirar `word_to_clean_html`/`word_to_clean_html_file` de
      `engine.py` (la condición para hacerlo, puesta en #45, ya se
      cumplió) — si algún test viejo dependía de esas funciones, adaptarlo
      o retirarlo también
- [ ] Actualizar/agregar tests de `test_api.py` para el endpoint
      `/convertir` usando el pipeline nuevo (puede mockear las llamadas a
      DeepSeek, igual que los tests unitarios de `ai_enhance.py` — no
      gastar tokens reales en CI)
- [ ] Nota de timeout: cada etapa que llama a DeepSeek tiene su propio
      timeout de 60s — en el peor caso (las 3 etapas necesitando la
      llamada real) la request puede tardar bastante. Confirmar que no
      hay un timeout más corto en el servidor/FastAPI que corte la
      request antes de tiempo

## Acceptance
- [ ] `uv run pytest` completo sigue pasando
- [ ] Probado a mano con `curl` real contra el endpoint: subir el mismo
      `.docx` de prueba, confirmar que el HTML de respuesta tiene el
      esqueleto completo (mismo resultado que ya confirmamos por script)

## Fuera de scope
- Frontend (issue aparte, después de este)
- Liquid (Etapa 4, issue aparte)
