import pytest

from app.models.base import LLMModel


class TestModel(LLMModel):
    @property
    def name(self) -> str:
        return "test-model"

    def generate(self, prompt: str) -> str:
        return f"Response to: {prompt}"


def test_model_interface():
    model = TestModel()

    assert model.name == "test-model"
    assert model.generate("Hello") == "Response to: Hello"


def test_model_interface_requires_implementation():
    with pytest.raises(TypeError):
        LLMModel()
