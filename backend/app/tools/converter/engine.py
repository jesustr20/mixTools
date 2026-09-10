"""
Motor de conversiones. Cada función es pura: recibe rutas, devuelve rutas.
Nada de FastAPI aquí -> se puede probar y reusar desde CLI, tests, etc.
"""
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

# LibreOffice headless NECESITA una carpeta $HOME escribible para crear su
# perfil de usuario. Si el proceso que lanza uvicorn no tiene HOME seteado
# (típico al correr como servicio/systemd/nohup), soffice se cuelga
# indefinidamente sin avisar. Forzamos un HOME propio y aislado por si acaso.
_LO_HOME = Path(tempfile.gettempdir()) / "libreoffice_home"
_LO_HOME.mkdir(exist_ok=True)


def _subprocess_env() -> dict:
    env = os.environ.copy()
    env["HOME"] = str(_LO_HOME)
    return env

import img2pdf
import pymupdf as fitz  # PyMuPDF (nombre nuevo, "fitz" queda deprecado)
from pypdf import PdfReader, PdfWriter


# ---------------------------------------------------------------------------
# PDF -> JPG
# ---------------------------------------------------------------------------
def pdf_to_jpg(pdf_path: Path, out_dir: Path, dpi: int = 150) -> list[Path]:
    """Rasteriza cada página del PDF a un JPG. Devuelve las rutas generadas."""
    doc = fitz.open(pdf_path)
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    output_paths = []
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=matrix)
        out_path = out_dir / f"{pdf_path.stem}_pagina_{i}.jpg"
        pix.save(out_path)
        output_paths.append(out_path)
    doc.close()
    return output_paths


def _next_name(base: str, used: dict[str, int]) -> str:
    """Devuelve `base` la primera vez y `base (n)` en colisiones, registrando el uso."""
    n = used.get(base, 0)
    used[base] = n + 1
    if n == 0:
        return base
    return f"{base} ({n})"


def batch_pdfs_to_jpg_zip(pdf_paths: list[Path], out_dir: Path, dpi: int = 150) -> Path:
    """Convierte varios PDFs a JPG y los empaqueta en un único zip organizado.

    - PDF de 1 página -> JPG suelto en la raíz, nombrado como el PDF
      (ej. ``recibo1.jpg``).
    - PDF de 2+ páginas -> carpeta con el nombre del PDF y adentro
      ``pagina_1.jpg``, ``pagina_2.jpg``, ...
    - Nombres duplicados: sufijo `` (1)``, `` (2)``... por separado para
      imágenes sueltas y carpetas.
    """
    stage = out_dir / "_stage"
    stage.mkdir()
    zip_path = out_dir / "conversion_mixtools.zip"
    used_files: dict[str, int] = {}
    used_folders: dict[str, int] = {}
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for idx, pdf_path in enumerate(pdf_paths):
            per_pdf = stage / f"{idx:03d}"
            per_pdf.mkdir()
            images = pdf_to_jpg(pdf_path, per_pdf, dpi=dpi)
            if len(images) == 1:
                name = _next_name(pdf_path.stem, used_files)
                zf.write(images[0], arcname=f"{name}.jpg")
            else:
                folder = _next_name(pdf_path.stem, used_folders)
                for i, image in enumerate(images, start=1):
                    zf.write(image, arcname=f"{folder}/pagina_{i}.jpg")
    return zip_path


# ---------------------------------------------------------------------------
# JPG/PNG -> PDF
# ---------------------------------------------------------------------------
def images_to_pdf(image_paths: list[Path], out_path: Path) -> Path:
    """Combina una o varias imágenes en un solo PDF (una imagen por página)."""
    with open(out_path, "wb") as f:
        f.write(img2pdf.convert([str(p) for p in image_paths]))
    return out_path


# ---------------------------------------------------------------------------
# Office (Word/Excel/PowerPoint) -> PDF  (vía LibreOffice headless)
# ---------------------------------------------------------------------------
def office_to_pdf(input_path: Path, out_dir: Path) -> Path:
    """
    Convierte docx/xlsx/pptx (y variantes .doc/.xls/.ppt) a PDF usando
    LibreOffice en modo headless. Es el mismo mecanismo que usan
    iLovePDF/Smallpdf por debajo.
    """
    cmd = [
        "soffice", "--headless", "--norestore",
        "--convert-to", "pdf",
        "--outdir", str(out_dir),
        str(input_path),
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120, env=_subprocess_env(), check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"LibreOffice falló: {result.stderr}")

    expected = out_dir / f"{input_path.stem}.pdf"
    if not expected.exists():
        raise RuntimeError("LibreOffice no generó el PDF esperado")
    return expected


# ---------------------------------------------------------------------------
# PDF -> Word editable
# ---------------------------------------------------------------------------
def pdf_to_word(pdf_path: Path, out_path: Path) -> Path:
    """
    Convierte PDF a DOCX intentando preservar el layout (párrafos, tablas
    simples). Funciona bien en PDFs de texto; en PDFs escaneados no hay
    OCR aquí (se podría añadir con pytesseract más adelante).
    """
    from pdf2docx import Converter

    cv = Converter(str(pdf_path))
    cv.convert(str(out_path))
    cv.close()
    return out_path


# ---------------------------------------------------------------------------
# Merge / Split / Comprimir
# ---------------------------------------------------------------------------
def merge_pdfs(pdf_paths: list[Path], out_path: Path) -> Path:
    writer = PdfWriter()
    for p in pdf_paths:
        reader = PdfReader(str(p))
        for page in reader.pages:
            writer.add_page(page)
    with open(out_path, "wb") as f:
        writer.write(f)
    return out_path


def split_pdf(pdf_path: Path, out_dir: Path) -> list[Path]:
    """Divide un PDF en un archivo por página."""
    reader = PdfReader(str(pdf_path))
    output_paths = []
    for i, page in enumerate(reader.pages, start=1):
        writer = PdfWriter()
        writer.add_page(page)
        out_path = out_dir / f"{pdf_path.stem}_pagina_{i}.pdf"
        with open(out_path, "wb") as f:
            writer.write(f)
        output_paths.append(out_path)
    return output_paths


def compress_pdf(pdf_path: Path, out_path: Path, image_quality: int = 40) -> Path:
    """
    Compresión real (no solo re-empaquetado): reduce la resolución/calidad
    de las imágenes embebidas usando Ghostscript, igual que iLovePDF.
    """
    cmd = [
        "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/ebook",  # balance calidad/tamaño razonable
        "-dNOPAUSE", "-dQUIET", "-dBATCH",
        f"-sOutputFile={out_path}", str(pdf_path),
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=120, env=_subprocess_env(), check=False
    )
    if result.returncode != 0 or not out_path.exists():
        raise RuntimeError(f"Ghostscript falló: {result.stderr}")
    return out_path
