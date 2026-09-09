---
slug: task-deepseek-harness
epic: epic-infra
title: "[Tech-task] Harness de DeepSeek en OpenCode (AGENTS.md + opencode.json)"
type: tech-task
labels: type:tech-task, area:infra, P0
milestone: MixTools v1
---
## Goal
Que DeepSeek ejecute tareas acotadas sin salirse de scope ni inventar
librerías/estructura que no se le pidió — mismo principio que ya seguimos a
mano en las conversiones de documentos ("nunca inventar estructura").

## Tasks
- [ ] `AGENTS.md` en la raíz del repo con reglas de scope, prohibición de
      tocar archivos fuera del módulo asignado, y obligación de dejar tests
      pasando
- [ ] `opencode.json` con DeepSeek como modelo por defecto y
      codebase-memory-mcp registrado como servidor MCP
- [ ] Probar con una tarea pequeña real (ej. un ajuste menor del módulo
      Word→HTML) antes de asignarle algo grande
