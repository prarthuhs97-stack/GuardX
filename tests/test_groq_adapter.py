import pytest

from app.models.adapters.groq_adapter import GroqAdapter


def test_groq_adapter_requires_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GROQ_API_KEY is not set"):
        GroqAdapter("openai/gpt-oss-20b")


def test_groq_adapter_name(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    adapter = GroqAdapter("openai/gpt-oss-20b")

    assert adapter.name == "openai/gpt-oss-20b"


def test_groq_adapter_generate(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    adapter = GroqAdapter("openai/gpt-oss-20b")

    class FakeMessage:
        content = "Mocked GuardX response"

    class FakeChoice:
        message = FakeMessage()

    class FakeResponse:
        choices = [FakeChoice()]

    def fake_create(**kwargs):
        assert kwargs["model"] == "openai/gpt-oss-20b"
        assert kwargs["messages"][0]["role"] == "user"
        assert kwargs["messages"][0]["content"] == "Test prompt"

        return FakeResponse()

    monkeypatch.setattr(
        adapter.client.chat.completions,
        "create",
        fake_create,
    )

    result = adapter.generate("Test prompt")

    assert result == "Mocked GuardX response"
