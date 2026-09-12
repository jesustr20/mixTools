---
slug: story-html-conventions
epic: epic-html-converter
title: "[Story] Word->HTML con fidelidad real y bloques de Liquid (arquitectura de 3 etapas)"
type: user-story
labels: type:user-story, area:html-converter, P1, gate:critica-pendiente
milestone: MixTools v1
---
**As a** usuario que convierte documentos de proyectos inmobiliarios
(contratos, anexos, fichas) a HTML para Sperant
**I want** una conversión fiel al Word original, con la estructura y clases
que ya uso, y que detecte automáticamente dónde va lógica de Liquid
**so that** no tenga que armar cada plantilla a mano desde cero como hago
hoy en chats sueltos.

## Arquitectura — 3 etapas

**Etapa 1 — Motor determinístico (sin IA, sin costo)**
Extracción profunda del `.docx`: leer XML crudo (no solo lo que da mammoth)
para sacar `w:shd fill` (colores reales), anchos de columna desde
`tblGrid`/twips, `gridSpan`/`vMerge` (colspan/rowspan), negritas, listas
reales vs. numeración escrita a mano. Deja el documento "similar" al Word
original en HTML plano.

**Etapa 2 — IA quirúrgica (DeepSeek)**
No reescribe todo — solo corrige lo puntual que la Etapa 1 no resolvió bien
(tablas con columnas fusionadas complejas, columnas simuladas con tabs,
casos raros). Usa el prompt de tablas (ver "Prompt de tablas" abajo) como
guía.

**Etapa 3 — Pasada de fidelidad final (IA, mismo proveedor)**
Revisa el resultado contra el Word original, corrige estructura si hace
falta, y aplica el esqueleto de salida fijo (ver "Esqueleto de salida"
abajo). Hallazgo de hoy: darle a la IA un **ejemplo concreto de esqueleto
ya bien armado** (no solo instrucciones en prosa) dio mejor resultado que
el prompt de texto solo — el prompt final debería combinar las dos cosas.

## IA por defecto — DeepSeek

- Jesús configura su propia API key de DeepSeek como variable de entorno
  del backend (mismo patrón que `AUTH_USER`/`AUTH_PASSWORD`)
- Transparente para los 6 compañeros — no ven ni configuran ninguna API
- Costo estimado bajísimo (documentos de puro texto, sin imágenes — pocos
  miles de tokens por conversión)
- Opción de traer tu propia clave (BYOK) queda para más adelante, no es
  necesaria para arrancar

## Esqueleto de salida (fijo, se reusa siempre)

Estructura de tabla `<thead>`/`<tfoot>`/`<tbody>` con clases fijas:
`.contenido`, `.cabecera`, `.pie_pagina`, `.espacio-cabecera`, `.espacio-pie`,
`.cuerpo-texto`, `.ajusTabla`, `.firmas`. Ver ejemplos reales ya construidos
en los hilos de trabajo (Ficha de Actualización de Datos, Convenio de
Separación) — sirven como referencia canónica para la Etapa 3.

## Prompt de tablas (a pulir, no crear de cero)

Ya existe un prompt largo explicando colspan/rowspan, colores exactos del
PDF/Word/Excel, y la regla de "no imaginar, no alucinar colores que no
estén en el original". Necesita pulirse — combinar con el enfoque de
ejemplo-de-esqueleto que funcionó mejor hoy.

## Catálogo de patrones Liquid

En vez de que la IA invente lógica de Liquid nueva cada vez, mantener un
catálogo de patrones ya resueltos: texto reconocible en el Word → bloque
Liquid exacto → de qué datos depende. Confirmados hoy:

1. **Clientes** (`budget.titulars`) — persona natural/jurídica, régimen de
   bienes mancomunados/unión de hecho, singular/plural con "y"/","
2. **Unidades** (`units`) — departamento vs. estacionamiento, piso vs.
   sótano, semisótano como caso especial (`floor == "0"`)
3. **Precios de unidad** (`price_units`) — moneda USD/Soles, número en
   letras, decimales — sigue la misma lógica de loop que "Unidades"
4. **Formas de pago** — pendiente, se agrega más adelante (no bloquea el
   resto — el catálogo crece con el tiempo, no hace falta completarlo de
   una vez)

## Acceptance (heredado + nuevo)
- [ ] `font-family` y `font-size` exactos del `.docx` fuente, no
      inventados
- [ ] Cero `&nbsp;` en la salida (espacio real o celda vacía)
- [ ] Tablas con `border-collapse: collapse`, anchos de `colgroup` reales
      (no inventados) desde el XML
- [ ] Ningún color/estilo que no exista en el documento fuente — "no
      imaginar, no alucinar"
- [ ] Al menos los 3 patrones de Liquid confirmados (clientes, unidades,
      precios) detectados y aplicados correctamente en un documento de
      prueba real

## Fuera de scope (por ahora)
- Patrón de "formas de pago" en Liquid — se agrega en una iteración
  posterior
- Imágenes/cuadros de texto flotantes complejos (documentos con esa
  estructura ya se resuelven manualmente por ahora)
