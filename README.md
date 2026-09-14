# MixTools

Reemplazo personal de iLovePDF + word2cleanhtml.com + Draftable, corriendo
en infraestructura propia. Sin suscripciones, sin límites mensuales, con
las mismas herramientas de fondo que usan esos servicios (LibreOffice,
Ghostscript, PyMuPDF) más un pipeline propio con IA para el conversor de
Word a HTML.

## En producción

| | URL |
|---|---|
| **Frontend** (la app) | https://mixtools-1.onrender.com |
| **Backend** (API) | https://mixtools.onrender.com |
| **Repo** | https://github.com/jesustr20/mixTools |

Protegido con usuario/contraseña (HTTP Basic Auth) — pedir credenciales al
dueño del proyecto. Los dos servicios corren en el plan gratis de
[Render](https://render.com) con auto-deploy: cualquier push a `main` los
actualiza solos en 1-2 minutos.

## Las 3 Herramientas

| Herramienta | Estado | Qué hace |
|---|---|---|
| **Conversor** | Completo | PDF a JPG, JPG a PDF, Office a PDF, PDF a Word, Dividir, Comprimir, Unir (7 utilidades) |
| **Word a HTML** | Backend completo, frontend con revelado progresivo | Convierte `.docx` a HTML fiel al original, con corrección de tablas y estructura semántica por IA |
| **Comparador** | Sin empezar | Comparar dos versiones de un documento y resaltar diferencias |

---

## Estructura del repo

```
mixtools/
├── backend/                     # FastAPI - Python 3.12, gestionado con uv
│   ├── Dockerfile                # LibreOffice + Ghostscript + la app
│   ├── app/
│   │   ├── main.py                # arma la app, registra las 3 Herramientas, aplica auth
│   │   ├── auth.py                 # HTTP Basic Auth (1 usuario compartido)
│   │   └── tools/
│   │       ├── converter/           # Herramienta 1 - engine.py + router.py
│   │       ├── html_converter/      # Herramienta 2 - ver detalle abajo
│   │       │   ├── structure.py       # Etapa 1: extraccion real del XML del .docx
│   │       │   ├── ai_enhance.py      # Etapas 2 y 3: correccion de tablas + esqueleto (IA)
│   │       │   └── router.py          # /convertir (todo junto) + /etapa1, /etapa2, /etapa3 (por separado)
│   │       └── comparator/          # Herramienta 3 - sin implementar todavia
│   └── tests/                    # pytest, todas las llamadas a IA mockeadas (cero costo en CI)
├── frontend/                     # React + TypeScript + Vite + Tailwind
│   └── src/
│       ├── lib/
│       │   ├── api.ts               # unico lugar que conoce las URLs del backend
│       │   └── auth.ts              # credenciales en memoria (nunca localStorage)
│       └── components/
│           ├── GenericConversionPanel.tsx   # utilidades simples del Conversor
│           ├── MergePdfsPanel.tsx           # Unir PDF (arrastrar para reordenar)
│           ├── WordToHtmlStagedPanel.tsx    # Word a HTML con revelado por etapa
│           └── LoginScreen.tsx              # gate de autenticacion
├── docs/
│   ├── issues/                  # cada issue del proyecto, un archivo .md por uno
│   ├── labels.yaml               # taxonomia de labels de GitHub
│   ├── design-tokens.md          # paleta de colores, tipografia, radios
│   └── setup-agentes.md          # como activar OpenCode + DeepSeek + el MCP de memoria de codigo
├── AGENTS.md                     # reglas que sigue DeepSeek al construir (anti-alucinacion, scope)
└── opencode.jsonc                # config de OpenCode (modelo, MCP servers)
```

---

## Correr en local

### Backend

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Requiere `LibreOffice` y `Ghostscript` instalados en el sistema (el
`Dockerfile` ya los instala para produccion; en local hay que tenerlos
aparte).

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

Por defecto apunta a `http://localhost:8000`. Para apuntar a otro backend,
crear un `.env` con `VITE_API_BASE=https://tu-backend`.

### Variables de entorno del backend

| Variable | Para que | Default en local |
|---|---|---|
| `AUTH_USER` | Usuario de la Basic Auth | `admin` (cambiar en produccion) |
| `AUTH_PASSWORD` | Contrasena de la Basic Auth | `changeme` (cambiar en produccion) |
| `DEEPSEEK_API_KEY` | Clave de la API de DeepSeek | vacio - sin ella, Word a HTML degrada a solo la Etapa 1, sin IA |

En Render, las tres se configuran en el dashboard del servicio backend
(**Environment**), no en ningun archivo del repo.

---

## El pipeline de Word a HTML, en detalle

Es la pieza mas compleja del proyecto - 3 etapas encadenadas (una cuarta,
Liquid, esta planeada pero no construida):

### Etapa 1 - Extraccion real (sin IA, structure.py)
Lee el XML crudo del `.docx` directamente (no usa mammoth ni ninguna
libreria de "conversion generica") para sacar: colores reales de celda
(incluyendo colores de tema con calculo de tint/shade), anchos de columna
exactos, colspan/rowspan reales, negrita/italica/subrayado leyendo el
valor real de cada propiedad (no solo si la etiqueta existe). Instantanea,
gratis, sin margen de error de IA.

### Etapa 2 - Correccion quirurgica de tablas (IA, ai_enhance.py)
Le pasa el HTML de la Etapa 1 a DeepSeek con un prompt especifico de
tablas complejas (colspan/rowspan que el motor deterministico no dedujo
bien). Instruccion explicita: corregir solo tablas, no reescribir el
resto del documento.

### Etapa 3 - Esqueleto + estructura semantica + fidelidad (IA)
Envuelve el contenido en el esqueleto de salida fijo (pensado para
insertarse dentro de Sperant - .cabecera, .pie_pagina, estructura de
tabla thead/tfoot/tbody) y aplica reglas de estructura:
- Titulos de documento/seccion -> clases genericas (.titulo-documento,
  .titulo-seccion)
- Enumeraciones con marcador ya escrito ("(i)", "1.") -> ol/li real, con
  el marcador conservado como texto literal
- Enumeraciones sin marcador (parrafos paralelos terminados en punto y
  coma) -> tambien se agrupan en lista, con numeracion/vinetas por CSS
  (seguro porque no hay texto que perder)
- Bloques de firma -> clase de centrado, sin borrar los guiones bajos
  literales
- Prohibido "corregir" errores tipograficos del original

### Nota de fidelidad (importante)
Despues de cada pasada de IA, una verificacion programatica
(_normalize_visible_text) compara el texto visible antes/despues - si el
modelo altero una sola letra, se descarta esa salida y se devuelve el
resultado de la etapa anterior sin tocar. Esto es lo que permite darle
libertad estructural a la IA (reordenar, agregar clases) sin arriesgar el
contenido real del documento - critico para uso legal/contractual.

### Endpoints
- `POST /api/html-converter/convertir` - pipeline completo, un solo
  pedido, devuelve el resultado final
- `POST /api/html-converter/etapa1`, `/etapa2`, `/etapa3` - cada etapa por
  separado, para el frontend con revelado progresivo (subis el archivo,
  ves la Etapa 1 casi al instante, y las siguientes van apareciendo
  automaticamente)

### Limitacion conocida - no determinismo
Los modelos de IA no son 100% predecibles: la misma entrada puede dar
resultados algo distintos entre llamadas (a veces aplica todas las reglas
bien, a veces se salta alguna, o en casos raros corta la respuesta a
mitad de camino). Pendiente: loguear el finish_reason real de la
respuesta de DeepSeek para diagnosticar con certeza por que a veces corta
antes de tiempo, y evaluar bajar la temperatura del modelo para reducir
la variabilidad.

---

## Backlog / proximos pasos

Ver `docs/issues/` para el detalle completo de cada uno. Los mas
relevantes pendientes:
- Etapa 4 (Liquid) - detectar patrones de texto ([bullet], blancos) e
  inyectar bloques for/variable segun un catalogo de patrones ya
  reconocidos (clientes, unidades, precios)
- Acceso multi-usuario real (hoy es 1 usuario/contrasena compartido para
  todo el equipo)
- Presets de calidad/resolucion para el Conversor (documentos grandes)
- Comparador - sin disenar todavia (spike pendiente: diff de texto vs.
  diff visual)
- Soporte de PDF/Excel como entrada para Word a HTML (hoy solo .docx)

---

## Metodologia de trabajo

Este proyecto se construye con 1 humano + 1 agente de IA (DeepSeek via
OpenCode), siguiendo un proceso de Definicion -> Critica -> Build por
cada pieza de trabajo, documentado como issues en docs/issues/ antes de
escribir codigo. Ver AGENTS.md para las reglas exactas que sigue el
agente (scope, tests obligatorios, nunca commitear directo a main).
