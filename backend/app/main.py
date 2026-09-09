"""
MixTools — tu propio "iLovePDF + word2cleanhtml + draftable" personal.

Arquitectura: cada Herramienta vive en app/tools/<nombre>/ con su propio
router.py (endpoints) y engine.py (lógica pura, sin FastAPI). Para agregar
una Herramienta 4 en el futuro: crea la carpeta, su router, y regístralo
aquí abajo con app.include_router(...). Nada más se toca.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.tools.comparator.router import router as comparator_router
from app.tools.converter.router import router as converter_router
from app.tools.html_converter.router import router as html_converter_router

app = FastAPI(
    title="MixTools",
    description="Conversor de archivos, Word→HTML limpio y Comparador de documentos — sin suscripciones.",
    version="0.1.0",
)

# En desarrollo local abrimos CORS a todo; cuando tengas el frontend en un
# dominio fijo, restringe allow_origins a esa URL.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(converter_router)
app.include_router(html_converter_router)
app.include_router(comparator_router)


@app.get("/api/health")
def health():
    return {"status": "ok", "herramientas": ["converter", "html_converter", "comparator"]}
