import pytest

from app.models.adapters.gemini_adapter import GeminiAdapter


def test_gemini_adapter_requires_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GEMINI_API_KEY is not set"):
        GeminiAdapter("gemini-2.5-flash")


def test_gemini_adapter_name(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    adapter = GeminiAdapter("gemini-2.5-flash")

    assert adapter.name == "gemini-2.5-flash"
