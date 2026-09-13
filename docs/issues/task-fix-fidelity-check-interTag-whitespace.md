---
slug: task-fix-fidelity-check-interTag-whitespace
epic: epic-html-converter
title: "[Bug] La verificación de fidelidad rechaza resultados válidos por espacios entre etiquetas (bloquea las mejoras de #69/#71)"
type: tech-task
labels: type:tech-task, area:html-converter, P0, gate:listo-para-build
milestone: MixTools v1
---
## Bug encontrado en producción real, con evidencia de log
Después de mergear #69 y #71 (listas, resaltado, títulos genéricos), el
resultado real sigue degradando al HTML plano de la Etapa 1, como si las
reglas nuevas nunca se hubieran aplicado. Log real:

```
DeepSeek alteró el texto del contenido; se descarta su salida...
len(entrada)=16688, len(salida)=16766
primer desajuste en el índice 22:
  entrada=[…CONVENIO DE SEPARACIÓNConste por el presente documento…]
  salida =[…CONVENIO DE SEPARACIÓN Conste por el presente documento…]
```

La ÚNICA diferencia es un espacio en blanco entre el `</p>` que cierra el
título y el `<p>` que abre el párrafo siguiente. El HTML de entrada no
tiene ningún espacio ahí (`<p>A</p><p>B</p>`, pegado); la salida del
modelo probablemente tiene un salto de línea de formato entre las
etiquetas (`<p>A</p>\n<p>B</p>`), que un navegador nunca renderiza como
espacio visible, pero que nuestra normalización actual sí cuenta como
texto real.

## Causa raíz confirmada
`_normalize_visible_text()` usa `_WHITESPACE_RE = re.compile(r"\s+")` que
**colapsa** corridas de espacios en uno solo, pero no puede detectar la
diferencia entre "cero espacios" (entrada) y "un espacio" (salida) — un
regex de colapso no puede borrar un espacio que aparece donde antes no
había ninguno.

## Fix
Antes de colapsar espacios internos del texto, **eliminar por completo**
cualquier espacio en blanco que esté directamente entre el cierre de una
etiqueta y la apertura de la siguiente (patrón `>(\s+)<` → `><`) — ese
espacio es puramente de formato/indentación del código, nunca se renderiza
visible en un navegador, así que es seguro descartarlo del todo en vez de
intentar que coincida exacto. El espacio DENTRO de un texto (entre
palabras) debe seguir comparándose con precisión, sin tocar esa parte de
la lógica.

## Tasks
- [ ] Agregar el paso de limpieza `>(\s+)<` → `><` en
      `_normalize_visible_text()`, ANTES de quitar las etiquetas (para que
      el patrón `>...<` siga siendo detectable)
- [ ] Test: dos HTML con el mismo contenido pero formato de indentación
      distinto entre etiquetas (uno compacto, uno con saltos de línea
      "bonitos") → deben normalizar al mismo texto
- [ ] Test: confirmar que el caso real de hoy (título + párrafo, con y sin
      salto de línea entre `</p><p>`) ya no se rechaza
- [ ] Confirmar que el test que SÍ debe rechazar (texto realmente distinto
      dentro de un párrafo) sigue rechazando correctamente — no se debe
      volver permisivo de más

## Acceptance
- [ ] `uv run pytest` completo sigue pasando
- [ ] Probado a mano con el documento real (Convenio de Separación): el
      resultado final ya no degrada, y muestra las mejoras de #69/#71
      (títulos con clase, listas reales, resaltado)
