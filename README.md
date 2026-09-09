# MixTools

Reemplazo personal de iLovePDF + word2cleanhtml.com + Draftable, corriendo en
infraestructura propia. Ver `backend/README.md` para instalar y correr el
backend.

## Estructura

```
mixtools/
├── backend/              # FastAPI — Conversor, Word→HTML, Comparador
├── frontend-preview/      # prototipo HTML/JS de la UI (pendiente Crítica)
├── docs/
│   ├── labels.yaml         # taxonomía de labels de GitHub
│   ├── issues/              # epics/stories/tech-tasks, uno por archivo
│   └── setup-agentes.md    # cómo activar OpenCode + DeepSeek + MCP
├── scripts/
│   ├── create-github-issues.sh  # crea todo docs/issues/ en tu repo real
│   ├── sync-labels.sh
│   ├── create_github_issues.py  # lógica (Python, sin dependencias)
│   └── sync_labels.py
├── .github/workflows/
│   ├── ci.yml               # lint + test del backend en cada PR
│   └── issue-ops.yml        # correr labels+issues desde la UI de Actions
├── AGENTS.md               # reglas para DeepSeek/OpenCode (anti-alucinación)
└── opencode.jsonc           # config de proyecto para OpenCode
```

## Módulos: monorepo, no "todo junto"

Un solo repo de Git — pero `backend/` y `frontend/` son módulos
independientes, no una app mezclada:

- **Cero imports cruzados.** Nada en `backend/` importa de `frontend/`, ni
  al revés. Se hablan únicamente por HTTP (`frontend/src/lib/api.ts` es el
  único punto de contacto).
- **Árboles de dependencias separados** — `backend/requirements.txt` (pip)
  y `frontend/package.json` (npm) no se mezclan.
- **CI separado por módulo** — `.github/workflows/ci.yml` (backend) y
  `ci-frontend.yml` (frontend) corren independientes; cada uno se salta
  solo si el PR no tocó su carpeta (job `changes`), sin quedar bloqueado
  esperando un check que nunca corre.
- Cada uno se puede correr, testear y — el día que haga falta — deployar
  por separado, aunque hoy viven en el mismo repo.

Si en algún momento el frontend necesita un ciclo de deploy totalmente
desacoplado del backend (ver ADR-0001, sección Next.js), separar en dos
repos es un cambio de infraestructura, no una reescritura — porque ya están
separados en todo lo que importa.



Este repo sigue el "Rail de Producto" de Jesús: Chispa → Definición → UX →
**Crítica** → **Alineación** → Spike/ADR → Build → Ship+medir, con Crítica y
Alineación como los únicos dos gates duros. El estado de cada gate se refleja
en labels (`gate:critica-pendiente`, `gate:alineacion-pendiente`,
`gate:listo-para-build`) sobre los issues en `docs/issues/`.

Con 1 humano + 1 IA en vez de 2 humanos, Crítica recae sobre Jesús (Claude no
puede criticar su propio spec/código). Ver `docs/issues/epic-infra.md` para
el detalle de esta adaptación.

## Flujo de trabajo módulo por módulo

1. Claude escribe la tarea concreta (issue en `docs/issues/` + prompt para el
   agente)
2. Jesús corre `./scripts/create-github-issues.sh` una vez que confirma el
   contenido
3. Jesús pega el prompt en OpenCode con DeepSeek como modelo
4. DeepSeek ejecuta con `codebase-memory-mcp` para no releer todo el repo,
   siguiendo las reglas de `AGENTS.md`
5. Jesús revisa el diff antes de mergear — Build sigue siendo PR → CI → merge

## Primer paso

Ver `docs/setup-agentes.md` para activar OpenCode + DeepSeek +
codebase-memory-mcp en tu máquina. El scaffolding de issues/labels ya está
probado en `--dry-run` — falta correrlo contra tu repo real de GitHub.
