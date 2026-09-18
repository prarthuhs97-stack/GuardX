from abc import ABC, abstractmethod


class LLMModel(ABC):
    """Common interface for all LLM adapters."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the model name."""
        pass

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from the model."""
        pass
