from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from app.tools.html_converter import ai_enhance
from app.utils.files import cleanup_now, cleanup_task, new_workspace, save_upload

router = APIRouter(prefix="/api/html-converter", tags=["Word a HTML"])


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
