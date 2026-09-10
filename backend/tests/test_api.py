"""Tests de API del Conversor (solo pdf-a-jpg, walking skeleton)."""
from pathlib import Path

import pymupdf as fitz
from fastapi.testclient import TestClient

from app.main import app


def _make_pdf(path: Path, pages: int) -> Path:
    """Genera un PDF real de `pages` páginas con PyMuPDF."""
    doc = fitz.open()
    for _ in range(pages):
        doc.new_page(width=200, height=200)
    doc.save(str(path))
    doc.close()
    return path


def test_pdf_a_jpg_endpoint(tmp_path: Path):
    client = TestClient(app)

    one_page = _make_pdf(tmp_path / "una_pagina.pdf", pages=1)
    with open(one_page, "rb") as f:
        response = client.post(
            "/api/converter/pdf-a-jpg",
            files={"file": ("una_pagina.pdf", f, "application/pdf")},
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/jpeg")

    three_pages = _make_pdf(tmp_path / "tres_paginas.pdf", pages=3)
    with open(three_pages, "rb") as f:
        response = client.post(
            "/api/converter/pdf-a-jpg",
            files={"file": ("tres_paginas.pdf", f, "application/pdf")},
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
