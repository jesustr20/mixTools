---
slug: task-codebase-memory-mcp
epic: epic-infra
title: "[Tech-task] Instalar codebase-memory-mcp y conectarlo a OpenCode"
type: tech-task
labels: type:tech-task, area:infra, P0
milestone: MixTools v1
---
## Goal
Que DeepSeek (vía OpenCode) consulte el grafo estructural del repo en vez de
leer archivos completos — reduce tokens y contexto ruidoso, que es la
principal fuente de alucinación en agentes baratos.

## Tasks
- [ ] `curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash`
- [ ] Confirmar que el instalador detectó OpenCode automáticamente
- [ ] Indexar el repo (`mixtools`) la primera vez
- [ ] Verificar con una consulta simple (ej. "qué funciones llaman a
      `office_to_pdf`") que el MCP responde antes de asignar tareas reales

## Notas de seguridad
Corre 100% local, no sube código a ningún lado — solo hace un chequeo de
versión contra la API de GitHub. Ver `SECURITY.md` del proyecto si quieres
auditar antes de instalar.
