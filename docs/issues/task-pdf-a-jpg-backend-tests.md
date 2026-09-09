---
slug: task-pdf-a-jpg-backend-tests
epic: epic-converter
title: "[Tech-task] Tests de PDF→JPG (walking skeleton, backend)"
type: tech-task
labels: type:tech-task, area:converter, P0, gate:listo-para-build
milestone: MixTools v1
---
## Goal
Primera rebanada de punta a punta. Solo `pdf-a-jpg`, nada más — es el
walking skeleton que valida todo el patrón (tests + CI + estructura) antes
de repetirlo con las otras 6 utilidades del Conversor.

## Tasks
- [ ] `pytest` + `httpx` en `requirements.txt`
- [ ] `backend/tests/converter/test_engine.py` — `test_pdf_to_jpg`:
      un PDF de 1 página -> 1 jpg válido (abrir con PIL/fitz y chequear
      dimensiones > 0); un PDF de 3 páginas -> 3 jpgs
- [ ] `backend/tests/test_api.py` — `test_pdf_a_jpg_endpoint`: POST real
      contra `/api/converter/pdf-a-jpg` con `TestClient`, verificar
      `content-type` de la respuesta
- [ ] Confirmar que `.github/workflows/ci.yml` corre estos tests (ya tiene
      el paso, solo faltaba que exista `tests/`)

## Acceptance
- [ ] `pytest backend/tests/converter/test_engine.py -k pdf_to_jpg` pasa en
      verde
- [ ] El PR de esto dispara el check `lint-and-test` en GitHub Actions

## Fuera de scope
Las otras 6 utilidades del Conversor — van una por una, en su propio issue,
después de que esta quede mergeada y probada.
