---
slug: epic-infra
title: "[Epic] Infraestructura de desarrollo (agentes + repo)"
type: epic
labels: type:epic, area:infra, P0
milestone: MixTools v1
---
## Capacidad de negocio
El tooling que permite trabajar módulo por módulo con Claude como planner y
DeepSeek (vía OpenCode) como agente de ejecución, sin gastar tokens de más
ni perder foco/alucinar.

## In scope
- Labels + issues creados por script (este mismo scaffolding)
- codebase-memory-mcp instalado y conectado a OpenCode
- Harness de DeepSeek (AGENTS.md) con reglas anti-alucinación y de scope
- Workflow de GitHub Actions para crear issues/labels sin hacerlo a mano

## Out of scope
- CI/CD de deploy (no aplica todavía, es una herramienta local)

## Status
En construcción — scaffolding de labels/issues/workflows completo.
**ADR-0001 resuelto** (arquitectura backend: vertical slices + hexagonal
liviano; frontend: React + TypeScript + Vite + Tailwind) — ver
`docs/adr/0001-arquitectura-backend-frontend.md`. Pendiente: instalar el
toolchain de agentes en la máquina de Jesús (task-codebase-memory-mcp,
task-deepseek-harness). El testing y el frontend avanzan módulo por módulo,
no de una — ver task-pdf-a-jpg-backend-tests / task-pdf-a-jpg-frontend como
primera rebanada, y epic-converter/epic-frontend para el resto.
