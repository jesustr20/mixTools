---
slug: task-fix-stage3-truncation
epic: epic-html-converter
title: "[Bug] Etapa 3 rechaza documentos largos (5+ páginas) — posible truncamiento por falta de max_tokens"
type: tech-task
labels: type:tech-task, area:html-converter, P0, gate:listo-para-build
milestone: MixTools v1
---
## Bug encontrado en producción real (Render)
Con un documento de 5 páginas (denso, texto legal), la Etapa 3 tardó
**3 minutos 16 segundos** y terminó rechazando la salida de DeepSeek por
no coincidir el texto visible — degradando al HTML sin esqueleto.

Log real:
```
18:43:32 → OPTIONS (preflight)
18:43:33 → Etapa 1 corriendo (python-docx)
18:46:49 → "DeepSeek alteró el texto del contenido; se descarta su salida"
18:46:49 → POST ... 200 OK
```

## Hipótesis principal (a confirmar)
Ninguna llamada a DeepSeek (`_deepseek_chat` en `ai_enhance.py`) fija un
`max_tokens` explícito en el payload — si la respuesta necesaria para
devolver un documento largo completo supera el límite por defecto del
modelo, la respuesta se **corta a la mitad**, y el texto truncado
lógicamente no coincide con el original al comparar — lo cual explicaría
tanto el rechazo como el tiempo largo (generó tokens hasta el techo).

## Gap de diagnóstico (arreglar primero, antes de "adivinar" el fix)
Hoy, cuando la Etapa 3 rechaza una salida, solo logueamos "alteró el
texto" — sin ningún detalle de **dónde** difieren los dos textos, ni sus
longitudes. Sin eso, no podemos confirmar la hipótesis de truncamiento
contra otras posibles causas (el modelo genuinamente reformuló algo, o un
bug en la normalización de `_normalize_visible_text`).

## Tasks
- [ ] Antes de aplicar cualquier fix: mejorar el log de rechazo en
      `apply_skeleton_and_verify` para incluir longitudes de ambos textos
      normalizados, y el punto exacto (índice/contexto) donde el primer
      carácter diverge — así confirmamos la causa real con evidencia, no
      suposición
- [ ] Si se confirma truncamiento: agregar `max_tokens` explícito al
      payload de `_deepseek_chat`, con un valor generoso (a definir según
      lo que confirme la documentación de DeepSeek para el modelo
      `deepseek-v4-pro` — no asumir un número sin verificar)
- [ ] Considerar: si el documento es muy largo, ¿vale la pena partir la
      Etapa 3 en fragmentos en vez de mandar todo de una? (evaluar
      complejidad vs. beneficio, puede quedar fuera de este issue si es
      mucho trabajo)
- [ ] Test: simular una respuesta mockeada truncada a propósito →
      confirmar que el log de rechazo ahora muestra el punto de
      divergencia con claridad

## Acceptance
- [ ] `uv run pytest` completo sigue pasando
- [ ] Probado a mano en Render con el mismo documento de 5 páginas que
      falló → confirmar que ahora sí llega con el esqueleto completo, en
      un tiempo razonable

## Fuera de scope
- Reducir el timeout de 60s por etapa (#51, issue aparte, relacionado pero
  distinto — ese es sobre el límite de Render, este es sobre el límite de
  tokens de DeepSeek)
