from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from app.tools.html_converter import ai_enhance, structure
from app.utils.files import cleanup_now, cleanup_task, new_workspace, save_upload

router = APIRouter(prefix="/api/html-converter", tags=["Word a HTML"])


class HtmlInput(BaseModel):
    html: str


@router.post("/etapa1")
def etapa1(file: UploadFile = File(...)):
    """Etapa 1 (sin IA): extrae la estructura del .docx y la devuelve como HTML."""
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(400, "Se esperaba un archivo .docx (Word)")
    ws = new_workspace()
    try:
        docx_path = save_upload(file, ws)
        html = structure.docx_to_html(docx_path)
        cleanup_now(ws)  # el HTML ya está en memoria, la carpeta no hace falta
        return {"html": html}
    except Exception:
        cleanup_now(ws)
        raise


@router.post("/etapa2")
def etapa2(body: HtmlInput):
    """Etapa 2 (IA): corrige tablas complejas. Degrada a la entrada si falla."""
    return {"html": ai_enhance.enhance_tables_with_ai(body.html)}


@router.post("/etapa3")
def etapa3(body: HtmlInput):
    """Etapa 3 (IA): envuelve en el esqueleto y verifica fidelidad."""
    return {"html": ai_enhance.apply_skeleton_and_verify(body.html)}


@router.post("/convertir")
def convertir(
    file: UploadFile = File(...),
    devolver_json: bool = Query(False, description="true = HTML en JSON, false = descarga .html"),
):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(400, "Se esperaba un archivo .docx (Word)")
    ws = new_workspace()
    try:
        docx_path = save_upload(file, ws)
        html = ai_enhance.word_to_html_full_pipeline(docx_path)
        if devolver_json:
            cleanup_now(ws)  # ya generamos el string en memoria, se puede borrar ya
            return JSONResponse({"html": html})
        out_path = ws / f"{docx_path.stem}.html"
        out_path.write_text(html, encoding="utf-8")
        return FileResponse(out_path, filename=out_path.name, media_type="text/html",
                             background=cleanup_task(ws))
    except Exception:
        cleanup_now(ws)
        raise
