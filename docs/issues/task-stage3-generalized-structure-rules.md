---
slug: task-stage3-generalized-structure-rules
epic: epic-html-converter
title: "[Story] Etapa 3 v2 — reglas generalizadas de estructura (títulos, listas, firmas) para CUALQUIER Word, con fidelidad estricta"
type: user-story
labels: type:user-story, area:html-converter, P0, gate:definicion-pendiente
milestone: MixTools v1
---
## Contexto
Se probó el mismo documento (Convenio de Separación) con dos enfoques:
1. DeepSeek en la Etapa 3 actual (#69) — aplicó las reglas de forma
   parcial e inconsistente (funcionó en una cláusula, se olvidó en otra)
2. Claude, con un prompt mucho más detallado y completo dado directo en
   el chat — generó una estructura completa y consistente (títulos con
   clase, listas reales en todo el documento, sub-ítems indentados,
   bloque de firmas centrado)

**La diferencia no es el modelo, es el nivel de detalle del prompt.** El
objetivo es llevar ese mismo nivel de detalle al prompt de la Etapa 3, en
términos de reglas generales por patrón (no ejemplos atados a un
documento puntual), para que cualquier IA detrás del pipeline llegue a un
resultado igual de completo y consistente.

## Hallazgo importante: ni Claude fue 100% fiel
Comparando texto carácter por carácter, el resultado de Claude tuvo 2
alteraciones reales (confirmado con `_normalize_visible_text`):
1. Corrigió un typo del Word original (`"Miraflores.."` → `"Miraflores."`)
   sin que se lo pidieran
2. Reemplazó una línea de firma hecha con guiones bajos literales
   (`_________`) por una línea de CSS (`border-top`), perdiendo esos
   caracteres del texto

**Estas dos cosas hay que evitarlas explícitamente en el prompt nuevo** —
la meta es la calidad visual de Claude, con la disciplina de fidelidad
estricta que ya tiene nuestro sistema.

## Reglas generalizadas propuestas (por patrón, no por documento)
1. **Título del documento**: el primer párrafo en negrita+subrayado,
   centrado, al inicio → clase genérica `.titulo-documento` (no
   `.titulo-convenio`, que asume que siempre es un convenio)
2. **Títulos de sección**: cualquier párrafo en negrita que empiece con
   una palabra tipo "CLÁUSULA", "ARTÍCULO", "SECCIÓN", "NUMERAL" (o
   patrón similar detectado por contexto) → clase genérica
   `.titulo-seccion`
3. **Listas enumeradas**: cualquier párrafo que empiece con un marcador
   de enumeración — `(i)`, `1.`, `(a)`, etc. — se convierte en `<ol>`/
   `<li>` real, **con el marcador conservado como texto literal dentro
   del `<li>`** (regla ya establecida en #69, debe aplicarse SIEMPRE, en
   TODAS las apariciones del documento, no solo la primera)
4. **Sub-ítems anidados**: marcadores de enumeración que aparecen DENTRO
   de otro ítem ya enumerado → clase genérica `.sub-item` con indentación,
   sin perder el marcador literal
5. **Bloques de firma**: una línea de guiones bajos seguida de un nombre
   e identificación → clase genérica `.firma-bloque` para centrar
   visualmente, **sin borrar los guiones bajos literales** — la línea
   real se mantiene como texto, el centrado es solo CSS alrededor
6. **Prohibición explícita**: nunca corregir errores tipográficos,
   puntuación duplicada, espacios de más, ni ningún otro "arreglo" no
   pedido — el texto se mantiene exactamente como está, errores incluidos

## Tasks
- [ ] Reescribir `_SKELETON_PROMPT` con las 6 reglas de arriba, en
      términos de patrones generales (no ejemplos de un documento
      puntual) — el prompt debe funcionar igual de bien en un Word
      distinto al de hoy
- [ ] Reforzar explícitamente: la regla se aplica en **cada aparición**
      del patrón en todo el documento, no solo la primera vez que
      aparece (corrige la inconsistencia observada en #69)
- [ ] Tests: al menos un test por regla (título de sección, lista con
      marcador conservado, sub-ítem anidado, firma con guiones
      conservados) usando fixtures sintéticos, no atados al documento de
      Convenio de Separación
- [ ] Test: confirmar que un "typo" a propósito en el HTML de entrada
      (ej. doble punto) sigue apareciendo igual en la salida — prueba
      explícita de que no se "corrige" nada
- [ ] Probado a mano con 2+ documentos Word DISTINTOS (no solo el
      Convenio de Separación) para confirmar que las reglas generalizan
      bien y no están sobreajustadas a un solo documento

## Acceptance
- [ ] `uv run pytest` completo sigue pasando
- [ ] Confirmado con al menos 2 documentos distintos: títulos de sección
      con clase, listas reales y consistentes en TODO el documento,
      firmas centradas sin perder los guiones bajos literales, cero
      "correcciones" de texto no pedidas
- [ ] La verificación de fidelidad existente sigue funcionando sin
      cambios — solo se amplía el prompt, no la lógica de comparación
