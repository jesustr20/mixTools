# Setup del toolchain de agentes (DeepSeek + OpenCode + codebase-memory-mcp)

Esto corre en **tu máquina**, no en el sandbox de Claude — necesita tus
credenciales (GitHub, DeepSeek).

## 1. GitHub CLI (para los scripts de issues/labels)

```bash
# si no lo tenés:
# https://cli.github.com/
gh auth login
```

## 2. OpenCode

```bash
curl -fsSL https://opencode.ai/install | bash   # confirmá el comando real en opencode.ai
opencode auth login    # elegí deepseek, pegá tu API key
```

## 3. codebase-memory-mcp

```bash
curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash
```

El instalador auto-detecta OpenCode y configura la entrada MCP solo. Confirmá:

```bash
opencode mcp list
# debería aparecer codebase-memory-mcp (o el nombre que le haya puesto)
```

Indexá el repo la primera vez (parado en la raíz del proyecto):

```bash
codebase-memory-mcp index .
# el comando exacto puede variar — correr `codebase-memory-mcp --help`
```

## 4. Crear labels + issues en tu repo real

```bash
chmod +x scripts/*.sh
./scripts/create-github-issues.sh tu-usuario/nombre-del-repo --dry-run   # primero en seco
./scripts/create-github-issues.sh tu-usuario/nombre-del-repo            # ya en serio
```

## 5. Primera tarea de prueba para DeepSeek

Antes de asignarle algo grande, probá con algo chico y verificable — por
ejemplo el ajuste de convenciones del módulo Word→HTML
(`story-html-conventions.md`). Yo te voy a ir armando el prompt exacto para
cada tarea cuando lleguemos a ese módulo — no hace falta que lo escribas vos.

## Orden recomendado

1. Este scaffolding (ya hecho acá)
2. Vos corrés los pasos 1–4 arriba, en tu máquina
3. Confirmás que `opencode mcp list` y `gh issue list` muestran lo esperado
4. Recién ahí arrancamos módulo por módulo — yo te doy el prompt, vos lo
   corrés en OpenCode, revisás el diff antes de aceptar
