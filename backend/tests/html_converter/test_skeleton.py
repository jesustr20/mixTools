"""Tests de la Etapa 3: esqueleto fijo + pasada de fidelidad (todo mockeado)."""
import logging
from pathlib import Path

import httpx

from app.tools.html_converter import ai_enhance
from app.tools.html_converter.ai_enhance import (
    _normalize_visible_text,
    apply_skeleton_and_verify,
    word_to_html_full_pipeline,
)

ORIGINAL = "<p>contenido</p>"


def _make_response(status_code: int, json_data: dict) -> httpx.Response:
    return httpx.Response(
        status_code,
        json=json_data,
        request=httpx.Request("POST", ai_enhance.DEEPSEEK_API_URL),
    )


def _ok_response(content: str) -> httpx.Response:
    return _make_response(200, {"choices": [{"message": {"content": content}}]})


def _wrap_in_skeleton(content: str) -> str:
    return (
        '<style type="text/css">.contenido{}</style>'
        '<div class="cabecera"></div>'
        '<table class="contenido">'
        '<thead><tr class="espacio-cabecera"><td> </td></tr></thead>'
        '<tfoot><tr><td><div class="espacio-pie"> </div></td></tr></tfoot>'
        '<tbody><tr><td class="cuerpo-texto">' + content + "</td></tr></tbody>"
        "</table>"
        '<div class="pie_pagina"></div>'
    )


def test_apply_skeleton_returns_model_content(monkeypatch):
    wrapped = _wrap_in_skeleton("<p>contenido</p>")
    captured = {}

    def fake_post(url, **kwargs):
        captured["payload"] = kwargs.get("json")
        return _ok_response(wrapped)

    monkeypatch.setattr(ai_enhance.httpx, "post", fake_post)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    result = apply_skeleton_and_verify(ORIGINAL)

    assert result == wrapped
    assert result.startswith("<style")
    system_prompt = captured["payload"]["messages"][0]["content"]
    user_content = captured["payload"]["messages"][1]["content"]
    assert user_content == ORIGINAL
    assert ".cuerpo-texto" in system_prompt
    assert ".cabecera" in system_prompt
    assert ".contenido" in system_prompt
    assert "reformules" in system_prompt  # regla de fidelidad explícita en el prompt


def test_apply_skeleton_preserves_visible_text(monkeypatch):
    """El texto visible de la salida debe ser idéntico al de la entrada."""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr(
        ai_enhance.httpx, "post", lambda *a, **k: _ok_response(_wrap_in_skeleton("<p>contenido</p>"))
    )

    result = apply_skeleton_and_verify(ORIGINAL)

    assert _normalize_visible_text(result) == _normalize_visible_text(ORIGINAL) == "contenido"


def test_apply_skeleton_rejects_altered_text(monkeypatch):
    """Si la IA reformula el texto, se descarta su salida y se devuelve la entrada."""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr(
        ai_enhance.httpx,
        "post",
        lambda *a, **k: _ok_response(_wrap_in_skeleton("<p>contenido MEJORADO</p>")),
    )

    result = apply_skeleton_and_verify(ORIGINAL)

    assert result == ORIGINAL


def test_apply_skeleton_truncated_output_logs_divergence(monkeypatch, caplog):
    """Issue #56: una respuesta truncada (cortada a la mitad) debe loguear el
    punto de divergencia con longitudes y contexto, para confirmar la causa."""
    body = "lorem ipsum dolor sit amet " * 40
    truncated_body = body[:400]  # cortado a propósito, a mitad de frase
    input_html = f"<p>{body}</p>"
    truncated_html = _wrap_in_skeleton(f"<p>{truncated_body}</p>")

    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr(ai_enhance.httpx, "post", lambda *a, **k: _ok_response(truncated_html))

    with caplog.at_level(logging.WARNING, logger="app.tools.html_converter.ai_enhance"):
        result = apply_skeleton_and_verify(input_html)

    assert result == input_html

    expected_input = _normalize_visible_text(input_html)
    expected_output = _normalize_visible_text(truncated_html)
    assert f"len(entrada)={len(expected_input)}" in caplog.text
    assert f"len(salida)={len(expected_output)}" in caplog.text
    assert f"primer desajuste en el índice {len(expected_output)}" in caplog.text


def test_apply_skeleton_missing_key_returns_input_unchanged(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("no debe llamarse a la API sin API key")

    monkeypatch.setattr(ai_enhance.httpx, "post", fail_if_called)

    assert apply_skeleton_and_verify(ORIGINAL) == ORIGINAL


def test_apply_skeleton_error_returns_input_unchanged(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    def raise_timeout(*args, **kwargs):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(ai_enhance.httpx, "post", raise_timeout)

    assert apply_skeleton_and_verify(ORIGINAL) == ORIGINAL


def test_full_pipeline_chains_stages(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr(ai_enhance, "docx_to_html", lambda path: "<p>stage1</p>")

    user_contents = []

    def fake_post(url, **kwargs):
        payload = kwargs.get("json")
        user_contents.append(payload["messages"][1]["content"])
        if payload["messages"][1]["content"] == "<p>stage1</p>":
            return _ok_response("<p>stage2</p>")
        return _ok_response(_wrap_in_skeleton("<p>stage2</p>"))

    monkeypatch.setattr(ai_enhance.httpx, "post", fake_post)

    result = word_to_html_full_pipeline(Path("documento.docx"))

    assert "cuerpo-texto" in result
    assert "<p>stage2</p>" in result
    assert user_contents == ["<p>stage1</p>", "<p>stage2</p>"]


def test_normalize_visible_text_strips_markup():
    html = (
        '<style type="text/css">body{color:red}</style>'
        '<div class="x">Hola <strong>mundo</strong></div> '
        "<!-- comentario -->"
        "<p>a&nbsp;b &amp; c</p>"
    )
    assert _normalize_visible_text(html) == "Hola mundo a b & c"
