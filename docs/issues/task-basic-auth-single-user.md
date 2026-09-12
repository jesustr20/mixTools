---
slug: task-basic-auth-single-user
epic: epic-infra
title: "[Tech-task] HTTP Basic Auth para 1 usuario (paso previo a la auth completa del equipo, #34)"
type: tech-task
labels: type:tech-task, area:infra, P0, gate:listo-para-build
milestone: MixTools v1
---
## Goal
Antes de deployar, proteger el backend con un usuario/contraseña simple
(solo Jesús, por ahora) para no dejarlo abierto en internet mientras se
sigue desarrollando. Esto es un paso previo y más chico que #34 (acceso
para las 6 personas del equipo) — no lo reemplaza, lo precede.

## Solución
`HTTPBasic` de FastAPI, credenciales desde variables de entorno
(`AUTH_USER`, `AUTH_PASSWORD`) — sin base de datos, sin librerías nuevas.
El navegador pide usuario/clave con su popup nativo la primera vez.

## Tasks
- [ ] Middleware/dependency de Basic Auth aplicado a todos los routers de
      `/api/*` (converter, html_converter, comparator) — no a `/api/health`
      ni a `/docs`, que pueden quedar públicos sin problema
- [ ] Variables de entorno `AUTH_USER` / `AUTH_PASSWORD` con un default
      solo para desarrollo local (documentado en el README como "cambiar
      en producción")
- [ ] Test: request sin credenciales → 401; con credenciales correctas →
      200; con credenciales incorrectas → 401

## Acceptance
- [ ] `uv run pytest` completo sigue pasando + los tests nuevos de auth
- [ ] Probado a mano: sin las credenciales correctas, cualquier endpoint
      de conversión rechaza el pedido

## Fuera de scope
- Múltiples usuarios / accesos por persona (eso es #34, para después)
- Proteger el frontend estático — solo el backend por ahora
