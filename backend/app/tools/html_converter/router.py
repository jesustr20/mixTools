from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from app.tools.html_converter import engine
from app.utils.files import cleanup_now, cleanup_task, new_workspace, save_upload

router = APIRouter(prefix="/api/html-converter", tags=["Word a HTML"])


@router.post("/convertir")
def convertir(
    file: UploadFile = File(...),
    strip_styles: bool = Query(True, description="Quitar estilos mso-* y font-family sueltos"),
    devolver_json: bool = Query(False, description="true = HTML en JSON, false = descarga .html"),
):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(400, "Se esperaba un archivo .docx (Word)")
    ws = new_workspace()
    try:
        docx_path = save_upload(file, ws)
        if devolver_json:
            html = engine.word_to_clean_html(docx_path, strip_styles=strip_styles)
            cleanup_now(ws)  # ya generamos el string en memoria, se puede borrar ya
            return JSONResponse({"html": html})
        out_path = ws / f"{docx_path.stem}.html"
        engine.word_to_clean_html_file(docx_path, out_path, strip_styles=strip_styles)
        return FileResponse(out_path, filename=out_path.name, media_type="text/html",
                             background=cleanup_task(ws))
    except Exception:
        cleanup_now(ws)
        raise
