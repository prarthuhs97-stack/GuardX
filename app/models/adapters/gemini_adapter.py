import os

from google import genai

from app.models.base import LLMModel


class GeminiAdapter(LLMModel):
    """Adapter for Google's Gemini API."""

    def __init__(self, model_name: str):
        self._model_name = model_name

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        self.client = genai.Client(api_key=api_key)

    @property
    def name(self) -> str:
        return self._model_name

    def generate(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self._model_name,
            contents=prompt,
        )

        return response.text
