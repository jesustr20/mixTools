from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.tools.comparator import engine
from app.utils.files import cleanup_now, new_workspace, save_upload

router = APIRouter(prefix="/api/comparator", tags=["Comparador"])

SUPPORTED = {".pdf", ".docx", ".xlsx", ".xlsm"}


@router.post("/comparar")
def comparar(archivo_a: UploadFile = File(...), archivo_b: UploadFile = File(...)):
    for f in (archivo_a, archivo_b):
        if Path(f.filename).suffix.lower() not in SUPPORTED:
            raise HTTPException(400, f"{f.filename}: tipo no soportado (usa pdf, docx o xlsx)")

    ws = new_workspace()
    try:
        path_a = save_upload(archivo_a, ws)
        path_b = save_upload(archivo_b, ws)
        try:
            resultado = engine.compare_files(path_a, path_b)
        except Exception as e:
            raise HTTPException(422, f"No se pudo comparar: {e}")
        return JSONResponse(resultado)
    finally:
        # Aquí sí se puede limpiar de inmediato: JSONResponse ya serializó
        # el contenido en memoria antes de retornar, no depende del disco.
        cleanup_now(ws)
