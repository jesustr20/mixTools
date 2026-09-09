"""
Herramienta 1: Conversor de archivos
Endpoints -> utilidades (así se ve reflejado en el frontend: una herramienta,
varias utilidades dentro).
"""
import zipfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.tools.converter import engine
from app.utils.files import cleanup_now, cleanup_task, new_workspace, save_upload

router = APIRouter(prefix="/api/converter", tags=["Conversor"])

OFFICE_EXTS = {".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods", ".odp"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


def _zip_files(paths: list[Path], zip_path: Path) -> Path:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in paths:
            zf.write(p, arcname=p.name)
    return zip_path


@router.post("/pdf-a-jpg")
def pdf_a_jpg(file: UploadFile = File(...), dpi: int = 150):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Se esperaba un archivo .pdf")
    ws = new_workspace()
    try:
        pdf_path = save_upload(file, ws)
        images = engine.pdf_to_jpg(pdf_path, ws, dpi=dpi)
        if len(images) == 1:
            return FileResponse(images[0], filename=images[0].name, background=cleanup_task(ws))
        zip_path = _zip_files(images, ws / f"{pdf_path.stem}_jpg.zip")
        return FileResponse(zip_path, filename=zip_path.name, background=cleanup_task(ws))
    except Exception:
        cleanup_now(ws)
        raise


@router.post("/jpg-a-pdf")
def jpg_a_pdf(files: list[UploadFile] = File(...)):
    ws = new_workspace()
    try:
        saved = []
        for f in files:
            if Path(f.filename).suffix.lower() not in IMAGE_EXTS:
                raise HTTPException(400, f"{f.filename} no es una imagen soportada")
            saved.append(save_upload(f, ws))
        out_path = ws / "convertido.pdf"
        engine.images_to_pdf(saved, out_path)
        return FileResponse(out_path, filename=out_path.name, background=cleanup_task(ws))
    except Exception:
        cleanup_now(ws)
        raise


@router.post("/office-a-pdf")
def office_a_pdf(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in OFFICE_EXTS:
        raise HTTPException(400, f"Extensión {ext} no soportada")
    ws = new_workspace()
    try:
        input_path = save_upload(file, ws)
        pdf_path = engine.office_to_pdf(input_path, ws)
        return FileResponse(pdf_path, filename=pdf_path.name, background=cleanup_task(ws))
    except Exception:
        cleanup_now(ws)
        raise


@router.post("/pdf-a-word")
def pdf_a_word(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Se esperaba un archivo .pdf")
    ws = new_workspace()
    try:
        pdf_path = save_upload(file, ws)
        out_path = ws / f"{pdf_path.stem}.docx"
        engine.pdf_to_word(pdf_path, out_path)
        return FileResponse(out_path, filename=out_path.name, background=cleanup_task(ws))
    except Exception:
        cleanup_now(ws)
        raise


@router.post("/merge")
def merge(files: list[UploadFile] = File(...)):
    ws = new_workspace()
    try:
        saved = []
        for f in files:
            if not f.filename.lower().endswith(".pdf"):
                raise HTTPException(400, f"{f.filename} no es PDF")
            saved.append(save_upload(f, ws))
        out_path = ws / "unido.pdf"
        engine.merge_pdfs(saved, out_path)
        return FileResponse(out_path, filename=out_path.name, background=cleanup_task(ws))
    except Exception:
        cleanup_now(ws)
        raise


@router.post("/split")
def split(file: UploadFile = File(...)):
    ws = new_workspace()
    try:
        pdf_path = save_upload(file, ws)
        parts = engine.split_pdf(pdf_path, ws)
        zip_path = _zip_files(parts, ws / f"{pdf_path.stem}_dividido.zip")
        return FileResponse(zip_path, filename=zip_path.name, background=cleanup_task(ws))
    except Exception:
        cleanup_now(ws)
        raise


@router.post("/comprimir")
def comprimir(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Se esperaba un archivo .pdf")
    ws = new_workspace()
    try:
        pdf_path = save_upload(file, ws)
        out_path = ws / f"{pdf_path.stem}_comprimido.pdf"
        engine.compress_pdf(pdf_path, out_path)
        return FileResponse(out_path, filename=out_path.name, background=cleanup_task(ws))
    except Exception:
        cleanup_now(ws)
        raise
