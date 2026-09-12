"""Tests de la Etapa 3: esqueleto fijo + pasada de fidelidad (todo mockeado)."""
from pathlib import Path

import httpx

from app.tools.html_converter import ai_enhance
from app.tools.html_converter.ai_enhance import (
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


def test_apply_skeleton_returns_model_content(monkeypatch):
    captured = {}

    def fake_post(url, **kwargs):
        captured["payload"] = kwargs.get("json")
        return _ok_response("<table class='contenido'><tbody><tr><td class='cuerpo-texto'><p>contenido</p></td></tr></tbody></table>")

    monkeypatch.setattr(ai_enhance.httpx, "post", fake_post)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    result = apply_skeleton_and_verify(ORIGINAL)

    assert result.startswith("<table")
    system_prompt = captured["payload"]["messages"][0]["content"]
    user_content = captured["payload"]["messages"][1]["content"]
    assert user_content == ORIGINAL
    assert ".cuerpo-texto" in system_prompt
    assert ".cabecera" in system_prompt
    assert ".contenido" in system_prompt
    assert "no renombres" in system_prompt or "NO renombres" in system_prompt


def test_apply_skeleton_missing_key_returns_input_unchanged(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("no debe llamarse a la API sin API key")

    monkeypatch.setattr(ai_enhance.httpx, "post", fail_if_called)

    result = apply_skeleton_and_verify(ORIGINAL)

    assert result == ORIGINAL


def test_apply_skeleton_error_returns_input_unchanged(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    def raise_timeout(*args, **kwargs):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(ai_enhance.httpx, "post", raise_timeout)

    result = apply_skeleton_and_verify(ORIGINAL)

    assert result == ORIGINAL


def test_full_pipeline_chains_stages(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setattr(ai_enhance, "docx_to_html", lambda path: "<p>stage1</p>")

    user_contents = []

    def fake_post(url, **kwargs):
        payload = kwargs.get("json")
        user_contents.append(payload["messages"][1]["content"])
        if payload["messages"][1]["content"] == "<p>stage1</p>":
            return _ok_response("<p>stage2</p>")
        return _ok_response("<div>stage3</div>")

    monkeypatch.setattr(ai_enhance.httpx, "post", fake_post)

    result = word_to_html_full_pipeline(Path("documento.docx"))

    assert result == "<div>stage3</div>"
    assert user_contents == ["<p>stage1</p>", "<p>stage2</p>"]
