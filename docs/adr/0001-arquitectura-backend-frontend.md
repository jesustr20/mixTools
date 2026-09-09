# ADR-0001: Arquitectura de backend y framework de frontend

**Status:** Aceptado — 2026-09-09
**Epic relacionado:** epic-infra

## Contexto

Antes de escalar a trabajo módulo por módulo con DeepSeek como agente de
ejecución, había que fijar dos decisiones caras de deshacer: cómo se
organiza el código del backend (¿DDD? ¿TDD? ¿SDD?) y qué framework de
frontend reemplaza al prototipo HTML plano.

## Decisión 1 — Arquitectura de backend

**Vertical slices + hexagonal liviano**, no DDD táctico completo.

Cada herramienta es una rebanada independiente: `engine.py` (lógica pura,
sin FastAPI) + `router.py` (HTTP). El dominio no depende del framework web.

**Por qué no DDD completo:** DDD táctico (agregados, entidades con
identidad, repositorios) se justifica cuando hay reglas de negocio
complejas y estado persistente con invariantes que proteger. Acá el flujo
es "archivo entra → se transforma → archivo sale", sin entidades con ciclo
de vida ni base de datos. Agregar esa ceremonia no compra nada. Lo que sí
se usa de DDD es lo estratégico: bounded contexts (los 3 módulos) y
lenguaje ubicuo ("herramienta", "utilidad", "conversión").

**Por qué esta arquitectura ayuda al trabajo con agentes:** la regla de
`AGENTS.md` de "una tarea = un módulo = una carpeta" solo es limpia de
cumplir si el código ya está cortado por módulo — que es justo esto.

### Testing — combinación, no un solo dogma

| Capa | Enfoque | Por qué |
|---|---|---|
| `engine.py` | TDD real | funciones puras, ideales para test-primero |
| `router.py` | Tests de contrato (TestClient) | regresión, no diseño — el endpoint ya existe y funciona |
| Conversión de documentos | Golden-file testing | es la versión-test de "nunca inventar estructura, verificar contra la fuente" |

**SDD:** ya lo veníamos haciendo sin nombrarlo — cada issue con
"Acceptance" en checklist es la spec. La diferencia real: cada ítem del
Acceptance se convierte en una aserción de test literal, no solo una
casilla marcada a ojo. Ejemplo: "cero `&nbsp;` en la salida" pasa a ser
`assert "&nbsp;" not in html`. Esto es lo que le da dientes al harness de
DeepSeek — cuando dice "listo", hay algo que lo verifica.

## Decisión 2 — Framework de frontend

**React + TypeScript + Vite + Tailwind**, portando el prototipo HTML ya
validado.

**Nota de corrección:** la primera versión de este ADR justificaba React
parcialmente por "DeepSeek alucina menos en frameworks con más
representación en su entrenamiento". Se verificó contra los benchmarks
actuales de DeepSeek V4 (SWE-bench Verified ~80%, a la par de modelos
cerrados de frontera en tareas agénticas) y ese argumento quedó débil — el
modelo ya no es el "eslabón débil" que esa justificación asumía. Se
mantiene React, pero por mérito propio:

- Es el plan original de Jesús antes de esta conversación
- TypeScript atrapa errores del agente vía el compilador — un crítico
  automático gratis, independiente de qué tan bueno sea el modelo
- El prototipo (estado en objeto + funciones `render*`) porta casi 1 a 1 a
  componentes + hooks, no es reescritura desde cero
- Sin librería de estado global (Redux/Zustand) — `useState`/`useReducer`
  alcanza para 3 herramientas con estado simple; agregar una sería
  sobre-ingeniería para este tamaño

**Testing:** Vitest + React Testing Library, mismo espíritu que el backend.

## Por qué el harness (`AGENTS.md`) se mantiene igual

No se armó porque DeepSeek fuera poco confiable — la razón correcta es que
incluso los agentes de código más fuertes de hoy muestran *reward hacking*
documentado en tareas largas (satisfacer el checklist sin resolver el
problema real). El harness es verificación para cualquier agente en tareas
largas, no un parche para un modelo débil. Se mantiene sin cambios.
