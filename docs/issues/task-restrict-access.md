---
slug: task-restrict-access
epic: epic-infra
title: "[Story] Restringir acceso a las 6 personas del equipo (evitar que cualquiera con el link entre)"
type: user-story
labels: type:user-story, area:infra, P2, gate:definicion-pendiente
milestone: MixTools v1
---
**As a** dueño de la herramienta, compartida con 6 compañeros de trabajo
**I want** que solo esas personas puedan usarla, no cualquiera que
encuentre la URL
**so that** no quede expuesta públicamente sin control de acceso.

## Por definir
- Mecanismo: ¿login simple (usuario/contraseña compartida), autenticación
  por dispositivo/IP fija de cada persona, o algo más simple tipo un token
  único por persona en la URL?
- Restringir por IP es frágil si trabajan remoto con IP dinámica — evaluar
  alternativas antes de comprometerse a esa vía.

## Fuera de scope (por ahora)
Implementación — este issue es un recordatorio para no perder el tema.
Se retoma después del deploy inicial y el límite de concurrencia, una vez
que el equipo ya esté probando la demo.
