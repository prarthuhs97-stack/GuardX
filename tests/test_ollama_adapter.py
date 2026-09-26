from app.models.adapters.ollama_adapter import OllamaAdapter


def test_ollama_adapter_name():
    adapter = OllamaAdapter("qwen2.5:0.5b")

    assert adapter.name == "qwen2.5:0.5b"


def test_ollama_adapter_generate(monkeypatch):
    adapter = OllamaAdapter("qwen2.5:0.5b")

    def fake_chat(**kwargs):
        assert kwargs["model"] == "qwen2.5:0.5b"
        assert kwargs["messages"][0]["role"] == "user"
        assert kwargs["messages"][0]["content"] == "Test prompt"

        return {
            "message": {
                "content": "Mocked local response",
            }
        }

    monkeypatch.setattr(
        "app.models.adapters.ollama_adapter.ollama.chat",
        fake_chat,
    )

    result = adapter.generate("Test prompt")

    assert result == "Mocked local response"


def test_ollama_adapter_uses_llm_model_interface():
    from app.models.base import LLMModel

    adapter = OllamaAdapter("gemma3:1b")

    assert isinstance(adapter, LLMModel)
