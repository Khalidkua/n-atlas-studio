from abc import ABC, abstractmethod
from typing import Any


class NAtlasProvider(ABC):
    """Common interface for all N-ATLaS inference providers."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a response from a text prompt."""
        raise NotImplementedError

    @abstractmethod
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        """Generate a response from chat messages."""
        raise NotImplementedError

    @abstractmethod
    def health(self) -> dict[str, Any]:
        """Return provider health information."""
        raise NotImplementedError
