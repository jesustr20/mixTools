"""Tests de API del Conversor (solo pdf-a-jpg, walking skeleton)."""
import io
import zipfile
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


def test_batch_pdf_a_jpg_endpoint(tmp_path: Path):
    client = TestClient(app)

    one_page = _make_pdf(tmp_path / "recibo1.pdf", pages=1)
    three_pages = _make_pdf(tmp_path / "recibo2.pdf", pages=3)

    with open(one_page, "rb") as f1, open(three_pages, "rb") as f2:
        response = client.post(
            "/api/converter/batch-pdf-a-jpg",
            files=[
                ("files", ("recibo1.pdf", f1, "application/pdf")),
                ("files", ("recibo2.pdf", f2, "application/pdf")),
            ],
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        assert set(zf.namelist()) == {
            "recibo1.jpg",
            "recibo2/pagina_1.jpg",
            "recibo2/pagina_2.jpg",
            "recibo2/pagina_3.jpg",
        }


def test_batch_pdf_a_jpg_endpoint_rejects_single_file(tmp_path: Path):
    client = TestClient(app)

    one_page = _make_pdf(tmp_path / "recibo1.pdf", pages=1)
    with open(one_page, "rb") as f:
        response = client.post(
            "/api/converter/batch-pdf-a-jpg",
            files=[("files", ("recibo1.pdf", f, "application/pdf"))],
        )

    assert response.status_code == 400
