"""Tests de la corrección de tablas con DeepSeek (Etapa 2). Todo mockeado."""
import httpx

from app.tools.html_converter import ai_enhance
from app.tools.html_converter.ai_enhance import enhance_tables_with_ai

ORIGINAL = "<p>original</p>"


def _make_response(status_code: int, json_data: dict) -> httpx.Response:
    return httpx.Response(
        status_code,
        json=json_data,
        request=httpx.Request("POST", ai_enhance.DEEPSEEK_API_URL),
    )


def _response_with_content(content: str) -> httpx.Response:
    return _make_response(200, {"choices": [{"message": {"content": content}}]})


def test_enhance_returns_model_content(monkeypatch):
    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["payload"] = kwargs.get("json")
        captured["headers"] = kwargs.get("headers")
        return _response_with_content("<html>corregido</html>")

    monkeypatch.setattr(ai_enhance.httpx, "post", fake_post)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    result = enhance_tables_with_ai(ORIGINAL)

    assert result == "<html>corregido</html>"
    assert captured["url"] == ai_enhance.DEEPSEEK_API_URL
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["payload"]["model"] == ai_enhance.DEEPSEEK_MODEL
    assert captured["payload"]["messages"][1]["content"] == ORIGINAL
    system_prompt = captured["payload"]["messages"][0]["content"]
    assert "coldspan" in system_prompt or "colspan" in system_prompt
    assert "do not change colors/values that are already correct" in system_prompt


def test_missing_key_returns_input_unchanged(monkeypatch):
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("no debe llamarse a la API sin API key")

    monkeypatch.setattr(ai_enhance.httpx, "post", fail_if_called)

    result = enhance_tables_with_ai(ORIGINAL)

    assert result == ORIGINAL


def test_timeout_returns_input_unchanged(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    def raise_timeout(*args, **kwargs):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(ai_enhance.httpx, "post", raise_timeout)

    result = enhance_tables_with_ai(ORIGINAL)

    assert result == ORIGINAL


def test_non_200_returns_input_unchanged(monkeypatch):
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    def return_error(*args, **kwargs):
        return _make_response(500, {"error": "boom"})

    monkeypatch.setattr(ai_enhance.httpx, "post", return_error)

    result = enhance_tables_with_ai(ORIGINAL)

    assert result == ORIGINAL
