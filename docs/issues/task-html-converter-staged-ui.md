---
slug: task-html-converter-staged-ui
epic: epic-html-converter
title: "[Story] Panel de Word→HTML con revelado progresivo por etapa (código en pantalla, no descarga)"
type: user-story
labels: type:user-story, area:html-converter, P0, gate:listo-para-build
milestone: MixTools v1
---
**As a** usuario que convierte documentos de trabajo
**I want** ver el resultado de cada etapa apenas está lista, en vez de
esperar a ciegas el pipeline completo
**so that** pueda elegir quedarme con un resultado más simple si me
alcanza, sin esperar innecesariamente las etapas de IA.

## Comportamiento esperado
- Subís el `.docx`, apretás "Convertir" una sola vez
- Aparece el **Proceso 1** (rápido, sin IA) con su resultado mostrado
  **como código HTML en pantalla** (tipo word2cleanhtml.com), con botón
  de copiar — nunca se descarga un archivo
- Automáticamente, sin que aprietes nada más, sigue el **Proceso 2**,
  mostrando su resultado debajo del Proceso 1 (que **no desaparece**)
- Lo mismo para el **Proceso 3**
- El usuario puede quedarse con el resultado de cualquiera de los
  procesos — todos quedan visibles y comparables a la vez, no se
  reemplazan entre sí

## Confirmado
- Requiere los 3 endpoints separados (ver issue de backend aparte)
- Es un componente nuevo — `GenericConversionPanel` no aplica
- Etapa 4 (Liquid) no existe todavía — dejar la UI preparada para sumar
  un cuarto bloque más adelante, pero no construirlo ahora

## Acceptance
- [ ] `npm run lint`, `npm run test`, `npm run build` pasan
- [ ] Probado a mano en el navegador: subir un `.docx` real, ver los 3
      resultados aparecer en fila automáticamente, cada uno con su botón
      de copiar, ninguno reemplaza al anterior

## Fuera de scope
- Etapa 4 / Liquid
- Cualquier cambio a las utilidades del Conversor
