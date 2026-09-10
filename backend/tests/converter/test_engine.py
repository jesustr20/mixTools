"""Tests de la lógica pura del Conversor (solo pdf_to_jpg, walking skeleton)."""
from pathlib import Path

import pymupdf as fitz

from app.tools.converter import engine


def _make_pdf(path: Path, pages: int) -> Path:
    """Genera un PDF real de `pages` páginas con PyMuPDF."""
    doc = fitz.open()
    for _ in range(pages):
        doc.new_page(width=200, height=200)
    doc.save(str(path))
    doc.close()
    return path


def _jpg_dimensions(path: Path) -> tuple[float, float]:
    doc = fitz.open(path)
    page = doc[0]
    dims = (page.rect.width, page.rect.height)
    doc.close()
    return dims


def test_pdf_to_jpg_single_page(tmp_path: Path):
    pdf = _make_pdf(tmp_path / "una_pagina.pdf", pages=1)
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    images = engine.pdf_to_jpg(pdf, out_dir)

    assert len(images) == 1
    width, height = _jpg_dimensions(images[0])
    assert width > 0
    assert height > 0


def test_pdf_to_jpg_multiple_pages(tmp_path: Path):
    pdf = _make_pdf(tmp_path / "tres_paginas.pdf", pages=3)
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    images = engine.pdf_to_jpg(pdf, out_dir)

    assert len(images) == 3
    for image in images:
        width, height = _jpg_dimensions(image)
        assert width > 0
        assert height > 0
