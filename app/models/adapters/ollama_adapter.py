import ollama

from app.models.base import LLMModel


class OllamaAdapter(LLMModel):
    """Adapter for locally running Ollama models."""

    def __init__(self, model_name: str):
        self._model_name = model_name

    @property
    def name(self) -> str:
        return self._model_name

    def generate(self, prompt: str) -> str:
        response = ollama.chat(
            model=self._model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response["message"]["content"]
