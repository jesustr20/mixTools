"""Tests de la lógica pura del Conversor (solo pdf_to_jpg, walking skeleton)."""
import threading
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pymupdf as fitz
from docx import Document

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


def _make_docx(path: Path) -> Path:
    """Genera un .docx real mínimo con python-docx."""
    doc = Document()
    doc.add_paragraph("Hola MixTools")
    doc.save(str(path))
    return path


def test_office_to_pdf_limits_concurrent_soffice_calls(tmp_path: Path, monkeypatch):
    """El semáforo debe impedir más de 3 procesos de soffice a la vez."""
    docx_path = _make_docx(tmp_path / "concurrencia.docx")
    out_dirs = []
    for i in range(5):
        d = tmp_path / f"out{i}"
        d.mkdir()
        out_dirs.append(d)

    counter_lock = threading.Lock()
    state = {"active": 0, "max_active": 0}

    real_run = engine.subprocess.run

    def tracked_run(*args, **kwargs):
        with counter_lock:
            state["active"] += 1
            state["max_active"] = max(state["max_active"], state["active"])
        try:
            time.sleep(0.5)
            return real_run(*args, **kwargs)
        finally:
            with counter_lock:
                state["active"] -= 1

    monkeypatch.setattr(engine.subprocess, "run", tracked_run)

    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = [
            ex.submit(engine.office_to_pdf, docx_path, out_dirs[i]) for i in range(5)
        ]
        results = [f.result(timeout=120) for f in futures]

    assert all(r.exists() for r in results)
    assert state["max_active"] <= 3
    assert state["max_active"] >= 3
