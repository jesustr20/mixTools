---
slug: task-frontend-deploy
epic: epic-infra
title: "[Tech-task] Deploy del frontend (pausado — Cloudflare está migrando Pages a Workers)"
type: tech-task
labels: type:tech-task, area:infra, P2, gate:definicion-pendiente
milestone: MixTools v1
---
## Estado
Pausado. Se intentó con Cloudflare Pages y se encontró que el producto está
en modo mantenimiento — Cloudflare está migrando todo a un modelo unificado
de Workers con Wrangler, que requiere `wrangler.toml` y configuración por
CLI en vez del flujo simple de "conectar Git y listo" que existía antes.

## Backend
Ya deployado y funcionando: `https://mixtools.onrender.com` (Render, Docker,
plan Free). Auth de un usuario activa (#37/#38). Confirmado con `/api/health`
y curl autenticado.

## Opciones evaluadas para el frontend
1. **Cloudflare Workers (nuevo modelo)** — requiere `wrangler.toml`,
   `npx wrangler deploy`, más configuración manual. Sigue soportando
   dominios personalizados, pero no es el flujo simple que se buscaba.
2. **Render Static Site** (misma cuenta que ya usa el backend) — más
   simple, sin salir de la plataforma ya validada. Tiene "Pull Request
   Previews": cada PR genera su propia URL automática
   (`algo-pr-N.onrender.com`), sin subdominio fijo configurable todavía
   (hay un feature request abierto en Render para eso, sin resolver).

## Próximos pasos (cuando se retome)
- [ ] Decidir entre Cloudflare Workers (más control, más setup) o Render
      Static Site (más simple, ya en la misma cuenta)
- [ ] Si es Render: crear el Static Site, activar PR Previews, apuntar
      `VITE_API_BASE` al backend real
- [ ] Dominio de producción (`mixtools.jesus-api.com` o el que se decida)
      recién al final, sobre la rama de producción

## Mientras tanto
Seguir trabajando local (laptop + WSL sincronizados por git), sin bloquear
el resto del desarrollo por esto.
