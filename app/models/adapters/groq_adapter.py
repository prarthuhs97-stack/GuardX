import os

from groq import Groq

from app.models.base import LLMModel


class GroqAdapter(LLMModel):
    """Adapter for Groq-hosted LLMs."""

    def __init__(self, model_name: str):
        self._model_name = model_name

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY is not set.")

        self.client = Groq(api_key=api_key)

    @property
    def name(self) -> str:
        return self._model_name

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self._model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content
