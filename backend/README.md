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

## Requisitos del sistema (no son pip)

```bash
sudo apt install libreoffice ghostscript
```

## Instalación

```bash
cd backend
pip install -r requirements.txt
```

## Levantar el servidor

```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Documentación interactiva (Swagger) automática en:
`http://localhost:8000/docs` — ahí puedes probar cada endpoint subiendo
archivos directo desde el navegador, sin frontend todavía.

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

### Herramienta 2 — Word a HTML (`/api/html-converter`)
| Endpoint | Qué hace |
|---|---|
| `POST /convertir?strip_styles=true&devolver_json=false` | DOCX -> HTML limpio (descarga .html o JSON) |

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
- **Frontend**: este backend está pensado para consumirse desde una app
  React con una vista por Herramienta y sus utilidades como pestañas/tabs
  dentro, tal como lo planteaste. El backend ya expone todo lo necesario
  vía HTTP + `/docs` para probarlo mientras se arma esa parte.
- **Multi-tenant/producción**: si algún día lo subes a un servidor
  (en vez de correrlo local), agrega autenticación básica antes de
  exponerlo a internet — ahora mismo cualquiera que llegue al puerto puede
  usarlo.
