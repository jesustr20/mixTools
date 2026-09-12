# MixTools

Tu "iLovePDF + word2cleanhtml + draftable" personal, sin suscripciones.
Corre 100% en tu máquina/servidor, con las mismas herramientas de fondo
que usan esos servicios (LibreOffice, Ghostscript, PyMuPDF).

## Arquitectura

```
backend/app/
├── main.py                     # arma la app y registra las 3 herramientas
├── tools/
│   ├── converter/               # Herramienta 1: conversor de archivos
│   │   ├── engine.py             # lógica pura (sin FastAPI)
│   │   └── router.py             # endpoints HTTP
│   ├── html_converter/          # Herramienta 2: Word -> HTML limpio
│   │   ├── engine.py
│   │   └── router.py
│   └── comparator/              # Herramienta 3: comparador de documentos
│       ├── engine.py
│       └── router.py
└── utils/files.py               # manejo de archivos temporales
```

Para agregar una Herramienta 4 en el futuro: crea `app/tools/nueva_herramienta/`
con su `engine.py` + `router.py`, y regístrala en `main.py` con
`app.include_router(...)`. El resto del proyecto no se toca.

## Requisitos del sistema (no son de uv)

```bash
sudo apt install libreoffice ghostscript
```

## Instalación

Usamos [uv](https://docs.astral.sh/uv/) (Astral) en vez de pip — más rápido,
y `uv.lock` fija versiones exactas (reproducible entre tu máquina, CI, y
cualquiera que clone el repo).

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
cd backend
uv sync
```

## Levantar el servidor

```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Nota WSL/Windows**: el `--host 0.0.0.0` es obligatorio en WSL2 — sin eso,
el servidor solo acepta conexiones desde dentro de la propia VM de Linux,
y el navegador de Windows (que técnicamente es "de afuera") se queda
colgado esperando sin error ni éxito. En Linux nativo no cambia nada, así
que el mismo comando sirve para las dos plataformas.

## Autenticación (Basic Auth)

Todos los endpoints de negocio bajo `/api/*` (converter, html-converter,
comparator) requieren autenticación básica HTTP: el navegador muestra su
popup nativo la primera vez. **`/api/health` y `/docs` quedan públicos.**

Las credenciales se leen de variables de entorno:

```bash
export AUTH_USER=jesus
export AUTH_PASSWORD=una-clave-fuerte
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- Si **no** definís `AUTH_USER`/`AUTH_PASSWORD`, se usa el default de
  desarrollo `admin` / `changeme`.
- **En cualquier entorno desplegado (producción, servidor, internet) es
  obligatorio** setear variables reales — dejarlo en `admin`/`changeme` es
  como no tener contraseña.

## Lint y tests

```bash
uv run ruff check app/
uv run pytest
```

Documentación interactiva (Swagger) automática en:
`http://localhost:8000/docs` — ahí puedes probar cada endpoint subiendo
archivos directo desde el navegador.

## Endpoints

### Herramienta 1 — Conversor (`/api/converter`)
| Endpoint | Qué hace |
|---|---|
| `POST /pdf-a-jpg?dpi=150` | PDF -> JPG (una imagen por página, o ZIP si son varias) |
| `POST /jpg-a-pdf` | Una o varias imágenes -> un PDF |
| `POST /office-a-pdf` | Word/Excel/PowerPoint -> PDF |
| `POST /pdf-a-word` | PDF -> DOCX editable |
| `POST /merge` | Varios PDF -> uno solo |
| `POST /split` | Un PDF -> ZIP con una página por archivo |
| `POST /comprimir` | Reduce el tamaño del PDF (calidad "ebook") |
| `POST /batch-pdf-a-jpg` | Varios PDFs a la vez -> `conversion_mixtools.zip` organizado |

### Herramienta 2 — Word a HTML (`/api/html-converter`)
| Endpoint | Qué hace |
|---|---|
| `POST /convertir?devolver_json=false` | DOCX -> HTML con esqueleto (descarga .html o JSON) |

### Herramienta 3 — Comparador (`/api/comparator`)
| Endpoint | Qué hace |
|---|---|
| `POST /comparar` | Compara `archivo_a` vs `archivo_b` (pdf/docx/xlsx en cualquier combinación) -> HTML con diff resaltado + estadísticas |

## Notas y próximos pasos

- **Diff visual (Fase 2)**: el comparador hoy compara TEXTO extraído (como
  el modo "inline" de Draftable). El diff 100% visual de Draftable
  (superposición de páginas como imágenes, detectar texto que se movió de
  posición) queda como siguiente iteración — está documentado como
  comentario al final de `app/tools/comparator/engine.py`.
- **OCR para PDFs escaneados**: `pdf-a-word` y el comparador funcionan sobre
  texto real del PDF. Si algún día necesitas convertir PDFs escaneados
  (imágenes), se agregaría `pytesseract` como utilidad nueva.
- **Frontend**: React + Vite + Tailwind, en `frontend/`. Cubre PDF→JPG
  (single y batch) hoy; el resto de las utilidades se van agregando
  módulo por módulo.
- **Multi-tenant/producción**: si algún día lo subes a un servidor
  (en vez de correrlo local), ya hay autenticación básica de un solo
  usuario (ver sección "Autenticación" arriba) como stopgap. La auth
  completa por equipo (6 personas, accesos individuales) es el issue #34,
  para después.
