---
slug: task-fix-bold-italic-detection
epic: epic-html-converter
title: "[Bug] Itálica (100% falso positivo) y negrita comparten el mismo bug ya arreglado para subrayado (#58)"
type: tech-task
labels: type:tech-task, area:html-converter, P0, gate:listo-para-build
milestone: MixTools v1
---
## Contexto importante
El PR #60 (que arregló #58, subrayado) investigó si `bold`/`italic` tenían
el mismo bug y concluyó que no ("Word no escribe w:val='none' para
itálica de forma sistemática"). **Esa conclusión era incorrecta** — se
confirma con evidencia real contra el mismo documento de prueba
(Convenio de Separación).

## Evidencia real (confirmada corriendo docx_to_html() + inspeccionando
## el XML crudo del mismo .docx)

**Itálica — 100% falso positivo:**
- `<em>` en la salida: 233
- Casos con `w:val="1"` o sin valor (SÍ es itálica real): **0**
- Casos con `w:val="0"` (NO es itálica): 303
- Es decir: ninguna de las 233 itálicas generadas es real

**Negrita — falso positivo real, menor pero presente:**
- Casos con `w:val="0"` (NO es negrita, pero el código actual la marca
  como negrita igual): 8
- Casos con `w:val="1"` o sin valor (SÍ es negrita real): 125

## Causa raíz (mismo patrón que #58, sin arreglar en las otras dos)
```python
bold = r_pr.find(qn("w:b")) is not None       # línea 221
italic = r_pr.find(qn("w:i")) is not None     # línea 222
```
Mismo problema que underline: chequea presencia de la etiqueta, no su
valor real.

## Fix
Aplicar el mismo patrón ya usado para underline (#58) a las tres
propiedades:
```python
def _is_flag_active(r_pr, tag_name: str) -> bool:
    el = r_pr.find(qn(tag_name))
    if el is None:
        return False
    val = el.get(qn("w:val"))
    return val not in ("0", "false", "none")

bold = _is_flag_active(r_pr, "w:b")
italic = _is_flag_active(r_pr, "w:i")
underline = ... # ya arreglado en #58, puede reusar la misma función si aplica
```

## Tasks
- [ ] Aplicar el fix a `bold` e `italic` (y considerar unificar underline
      en la misma función auxiliar si tiene sentido, ya que las tres
      comparten la lógica ahora)
- [ ] Tests con los 3 casos por propiedad (val="0", val="1"/sin valor,
      elemento ausente) — igual que se hizo para underline en #58/#60
- [ ] Correr contra el documento real de prueba (Convenio de Separación)
      y confirmar: 0 `<em>` de más (el documento no debería tener ninguna
      itálica real), y la negrita coincide con lo que realmente está en
      negrita en el Word original

## Acceptance
- [ ] `uv run pytest` completo sigue pasando
- [ ] Confirmado contra el documento real: cantidad de `<em>` baja a 0 (o
      al número real de itálicas legítimas, si las hubiera)
