"""Tests de API del Conversor (solo pdf-a-jpg, walking skeleton)."""
import io
import zipfile
from pathlib import Path

import pymupdf as fitz
import pytest
from fastapi.testclient import TestClient

from app.main import app

AUTH_USER = "testuser"
AUTH_PASSWORD = "testpass"
AUTH = (AUTH_USER, AUTH_PASSWORD)


@pytest.fixture(autouse=True)
def _set_auth_env(monkeypatch):
    """Fija credenciales conocidas para todos los tests (no admin/changeme)."""
    monkeypatch.setenv("AUTH_USER", AUTH_USER)
    monkeypatch.setenv("AUTH_PASSWORD", AUTH_PASSWORD)


def _make_pdf(path: Path, pages: int) -> Path:
    """Genera un PDF real de `pages` páginas con PyMuPDF."""
    doc = fitz.open()
    for _ in range(pages):
        doc.new_page(width=200, height=200)
    doc.save(str(path))
    doc.close()
    return path


def _make_png(path: Path, width: int, height: int) -> Path:
    """Genera un PNG real de las dimensiones dadas con PyMuPDF."""
    doc = fitz.open()
    page = doc.new_page(width=width, height=height)
    pix = page.get_pixmap()
    pix.save(str(path))
    doc.close()
    return path


def test_pdf_a_jpg_endpoint(tmp_path: Path):
    client = TestClient(app)

    one_page = _make_pdf(tmp_path / "una_pagina.pdf", pages=1)
    with open(one_page, "rb") as f:
        response = client.post(
            "/api/converter/pdf-a-jpg",
            files={"file": ("una_pagina.pdf", f, "application/pdf")},
            auth=AUTH,
        )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/jpeg")

    three_pages = _make_pdf(tmp_path / "tres_paginas.pdf", pages=3)
    with open(three_pages, "rb") as f:
        response = client.post(
            "/api/converter/pdf-a-jpg",
            files={"file": ("tres_paginas.pdf", f, "application/pdf")},
            auth=AUTH,
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
            auth=AUTH,
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
            auth=AUTH,
        )

    assert response.status_code == 400


def test_batch_pdf_a_jpg_same_name_different_pages(tmp_path: Path):
    client = TestClient(app)

    one_page = _make_pdf(tmp_path / "one.pdf", pages=1)
    three_pages = _make_pdf(tmp_path / "three.pdf", pages=3)

    with open(one_page, "rb") as f1, open(three_pages, "rb") as f2:
        response = client.post(
            "/api/converter/batch-pdf-a-jpg",
            files=[
                ("files", ("recibo.pdf", f1, "application/pdf")),
                ("files", ("recibo.pdf", f2, "application/pdf")),
            ],
            auth=AUTH,
        )

    assert response.status_code == 200
    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        assert set(zf.namelist()) == {
            "recibo.jpg",
            "recibo/pagina_1.jpg",
            "recibo/pagina_2.jpg",
            "recibo/pagina_3.jpg",
        }


def test_merge_same_name(tmp_path: Path):
    client = TestClient(app)

    one_page = _make_pdf(tmp_path / "one.pdf", pages=1)
    three_pages = _make_pdf(tmp_path / "three.pdf", pages=3)

    with open(one_page, "rb") as f1, open(three_pages, "rb") as f2:
        response = client.post(
            "/api/converter/merge",
            files=[
                ("files", ("recibo.pdf", f1, "application/pdf")),
                ("files", ("recibo.pdf", f2, "application/pdf")),
            ],
            auth=AUTH,
        )

    assert response.status_code == 200
    doc = fitz.open(stream=response.content, filetype="pdf")
    assert doc.page_count == 4
    doc.close()


def test_jpg_a_pdf_same_name(tmp_path: Path):
    client = TestClient(app)

    small = _make_png(tmp_path / "small.png", width=100, height=100)
    big = _make_png(tmp_path / "big.png", width=200, height=200)

    with open(small, "rb") as f1, open(big, "rb") as f2:
        response = client.post(
            "/api/converter/jpg-a-pdf",
            files=[
                ("files", ("foto.png", f1, "image/png")),
                ("files", ("foto.png", f2, "image/png")),
            ],
            auth=AUTH,
        )

    assert response.status_code == 200
    doc = fitz.open(stream=response.content, filetype="pdf")
    assert doc.page_count == 2
    widths = [page.rect.width for page in doc]
    doc.close()
    assert widths[0] < widths[1]


def _post_pdf_a_jpg(tmp_path: Path, auth=None):
    client = TestClient(app)
    pdf = _make_pdf(tmp_path / "una_pagina.pdf", pages=1)
    with open(pdf, "rb") as f:
        return client.post(
            "/api/converter/pdf-a-jpg",
            files={"file": ("una_pagina.pdf", f, "application/pdf")},
            auth=auth,
        )


def test_health_is_public():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200


def test_auth_required_no_credentials(tmp_path: Path):
    response = _post_pdf_a_jpg(tmp_path)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"


def test_auth_correct_credentials(tmp_path: Path):
    response = _post_pdf_a_jpg(tmp_path, auth=AUTH)
    assert response.status_code == 200


def test_auth_wrong_credentials(tmp_path: Path):
    response = _post_pdf_a_jpg(tmp_path, auth=(AUTH_USER, "password-incorrecta"))
    assert response.status_code == 401
