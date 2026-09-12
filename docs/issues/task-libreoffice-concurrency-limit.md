---
slug: task-libreoffice-concurrency-limit
epic: epic-infra
title: "[Tech-task] Limitar conversiones simultáneas de LibreOffice (evitar que 6 personas usándolo a la vez tumben el servidor)"
type: tech-task
labels: type:tech-task, area:infra, P0, gate:listo-para-build
milestone: MixTools v1
---
## Goal
Con hasta 6 personas usando la herramienta de forma remota e impredecible,
si 2+ convierten un Office→PDF al mismo tiempo, cada una dispara su propio
proceso de LibreOffice — pesado en memoria. Sin límite, esto puede agotar
la RAM del servidor y colgar el servicio para todos.

## Confirmado técnicamente
- `office_to_pdf()` (`backend/app/tools/converter/engine.py`, líneas
  99-125) es la **única** función que invoca `soffice` (línea 106).
  Ninguna otra conversión (PDF→JPG, JPG→PDF, split, merge, comprimir) usa
  LibreOffice — el límite va solo ahí, no en todo el motor.

## Solución
Un `threading.Semaphore` a nivel de módulo, envolviendo el bloque que
llama a `soffice`. No hace falta Redis/Celery/cola externa — el semáforo
vive en memoria del propio proceso, suficiente para una sola instancia de
backend sirviendo a un equipo de este tamaño.

```python
import threading
office_semaphore = threading.Semaphore(3)  # valor a confirmar en Build

def office_to_pdf(input_path: Path, out_dir: Path) -> Path:
    with office_semaphore:
        # ... llamada a soffice existente, sin cambios ...
```

Si llegan más de 3 pedidos simultáneos, el 4to y siguientes esperan su
turno automáticamente (sin error, sin que el usuario haga nada) hasta que
se libere un lugar — típicamente unos segundos, no minutos.

## Tasks
- [ ] Agregar el semáforo en `office_to_pdf()` como arriba
- [ ] Test: simular 5 llamadas concurrentes a `office_to_pdf()` (con
      `concurrent.futures.ThreadPoolExecutor` o similar) y confirmar que
      nunca hay más de 3 ejecutando `soffice` al mismo tiempo (se puede
      instrumentar con un contador que se incrementa/decrementa alrededor
      de la llamada real, verificando que el máximo observado sea 3)
- [ ] Confirmar que los tests existentes de `office-a-pdf` (si los hay)
      siguen pasando

## Acceptance
- [ ] `uv run pytest` completo sigue pasando
- [ ] El nuevo test de concurrencia confirma el límite de 3 simultáneas
- [ ] Probado a mano: 5 conversiones Office→PDF disparadas casi a la vez
      (ej. 5 pestañas del navegador) → todas terminan bien, ninguna falla,
      las últimas simplemente tardan un poco más

## Fuera de scope
- Cola persistente/externa (Redis, Celery) — innecesaria a esta escala
- Cambios a cualquier endpoint que no use LibreOffice
- El tema de restricción de acceso por usuario (#34, aparte)
