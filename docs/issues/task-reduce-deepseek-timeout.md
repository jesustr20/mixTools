---
slug: task-reduce-deepseek-timeout
epic: epic-html-converter
title: "[Tech-task] Reducir timeout de DeepSeek para no chocar con el límite de ~100s de Render"
type: tech-task
labels: type:tech-task, area:html-converter, P2, gate:listo-para-build
milestone: MixTools v1
---
## Riesgo encontrado (en #50)
Cada etapa del pipeline Word→HTML que llama a DeepSeek tiene un timeout de
60s. En el peor caso (las 3 etapas necesitando la llamada real, cada una
tardando el máximo), la request total podría llegar a ~180s — pero Render
(donde está el backend desplegado) corta requests a los ~100s por su load
balancer.

En la práctica, las pruebas manuales mostraron que cada etapa tarda
segundos, no cerca del límite de 60s — así que el riesgo es bajo hoy, pero
vale la pena ajustar antes de que sea un problema real con documentos más
grandes o momentos de latencia alta de la API.

## Fix propuesto
Bajar `TIMEOUT_SECONDS` en `ai_enhance.py` a algo como 25-30s por etapa
(dejando margen: 3 × 30s = 90s, bajo el límite de Render), y considerar si
hace falta un timeout total del pipeline completo, no solo por etapa.

## Fuera de scope
No es urgente — se retoma si empieza a haber timeouts reales en uso.
