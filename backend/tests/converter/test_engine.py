"""Tests de la lógica pura del Conversor (solo pdf_to_jpg, walking skeleton)."""
import zipfile
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


def _zip_names(zip_path: Path) -> set[str]:
    with zipfile.ZipFile(zip_path) as zf:
        return set(zf.namelist())


def _make_pdfs_same_name(root: Path, pages_list: list[int]) -> list[Path]:
    """Crea varios PDFs con el mismo nombre (`recibo.pdf`) en subcarpetas distintas."""
    paths = []
    for i, pages in enumerate(pages_list):
        subdir = root / f"d{i}"
        subdir.mkdir()
        paths.append(_make_pdf(subdir / "recibo.pdf", pages=pages))
    return paths


def test_batch_two_single_page_pdfs(tmp_path: Path):
    p1 = _make_pdf(tmp_path / "recibo1.pdf", pages=1)
    p2 = _make_pdf(tmp_path / "recibo2.pdf", pages=1)
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    zip_path = engine.batch_pdfs_to_jpg_zip([p1, p2], out_dir)

    assert zip_path.name == "conversion_mixtools.zip"
    assert _zip_names(zip_path) == {"recibo1.jpg", "recibo2.jpg"}


def test_batch_one_single_one_multi_page_pdf(tmp_path: Path):
    p1 = _make_pdf(tmp_path / "recibo1.pdf", pages=1)
    p2 = _make_pdf(tmp_path / "recibo2.pdf", pages=3)
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    zip_path = engine.batch_pdfs_to_jpg_zip([p1, p2], out_dir)

    assert _zip_names(zip_path) == {
        "recibo1.jpg",
        "recibo2/pagina_1.jpg",
        "recibo2/pagina_2.jpg",
        "recibo2/pagina_3.jpg",
    }


def test_batch_mixed_three_or_more_pdfs(tmp_path: Path):
    p1 = _make_pdf(tmp_path / "a.pdf", pages=1)
    p2 = _make_pdf(tmp_path / "b.pdf", pages=2)
    p3 = _make_pdf(tmp_path / "c.pdf", pages=4)
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    zip_path = engine.batch_pdfs_to_jpg_zip([p1, p2, p3], out_dir)

    assert _zip_names(zip_path) == {
        "a.jpg",
        "b/pagina_1.jpg",
        "b/pagina_2.jpg",
        "c/pagina_1.jpg",
        "c/pagina_2.jpg",
        "c/pagina_3.jpg",
        "c/pagina_4.jpg",
    }


def test_batch_duplicate_names_two_single_page(tmp_path: Path):
    pdfs = _make_pdfs_same_name(tmp_path, [1, 1])
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    zip_path = engine.batch_pdfs_to_jpg_zip(pdfs, out_dir)

    assert _zip_names(zip_path) == {"recibo.jpg", "recibo (1).jpg"}


def test_batch_duplicate_names_single_and_multi_page(tmp_path: Path):
    pdfs = _make_pdfs_same_name(tmp_path, [1, 3])
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    zip_path = engine.batch_pdfs_to_jpg_zip(pdfs, out_dir)

    assert _zip_names(zip_path) == {
        "recibo.jpg",
        "recibo/pagina_1.jpg",
        "recibo/pagina_2.jpg",
        "recibo/pagina_3.jpg",
    }


def test_batch_duplicate_names_three_pdfs_ordered(tmp_path: Path):
    pdfs = _make_pdfs_same_name(tmp_path, [1, 1, 1])
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    zip_path = engine.batch_pdfs_to_jpg_zip(pdfs, out_dir)

    with zipfile.ZipFile(zip_path) as zf:
        assert zf.namelist() == ["recibo.jpg", "recibo (1).jpg", "recibo (2).jpg"]
