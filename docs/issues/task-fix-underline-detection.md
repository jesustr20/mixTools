---
slug: task-fix-underline-detection
epic: epic-html-converter
title: "[Bug] Etapa 1 detecta subrayado en casi todo el documento — no revisa el valor de w:u, solo su presencia"
type: tech-task
labels: type:tech-task, area:html-converter, P0, gate:listo-para-build
milestone: MixTools v1
---
## Bug encontrado y confirmado con evidencia real
Con un documento real (Convenio de Separación, sin ningún subrayado
visible en Word), la Etapa 1 sola (sin ninguna IA de por medio) generó
229 etiquetas `<u>` — confirmado corriendo `docx_to_html()` aislada contra
el `.docx` real, sin pasar por Etapa 2/3.

## Causa raíz confirmada (structure.py, línea 223)
```python
underline = r_pr.find(qn("w:u")) is not None
```
Esto chequea si la etiqueta `<w:u>` **existe**, no qué valor tiene. Word
siempre escribe `<w:u>` en cada run, incluso para runs SIN subrayado —
en ese caso, con `w:val="none"`:
```xml
<w:u w:val="none"/>
```
Confirmado en el XML real del documento de prueba: prácticamente todo el
cuerpo del texto tiene `w:val="none"`, y el código actual lo trata como
"sí tiene subrayado" de todas formas.

## Fix
```python
u_el = r_pr.find(qn("w:u"))
underline = u_el is not None and u_el.get(qn("w:val")) not in (None, "none", "0", "false")
```

## Tasks
- [ ] Aplicar el fix de arriba (o equivalente) en `_extract_run` (o como se
      llame la función en la línea 223)
- [ ] Test con un `.docx` real o generado programáticamente que tenga:
      un run con `w:u w:val="none"` (no debe dar `<u>`), un run con
      `w:u w:val="single"` (sí debe dar `<u>`), y un run sin ninguna
      etiqueta `<w:u>` en absoluto (no debe dar `<u>`)
- [ ] Confirmar que el resto de los tests de `test_structure.py` (que
      probablemente asumían el comportamiento viejo) siguen teniendo
      sentido — si alguno pasaba "por accidente" gracias al bug, ajustarlo

## Acceptance
- [ ] `uv run pytest` completo sigue pasando
- [ ] Corrido contra el documento real de prueba (Convenio de Separación)
      → 0 (o muy pocas, si alguna es legítima) apariciones de `<u>` en la
      salida de la Etapa 1 sola
