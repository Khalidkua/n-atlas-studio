from typing import Any

from .base import NAtlasProvider


class MockProvider(NAtlasProvider):
    """Development provider used before connecting a real N-ATLaS backend."""

    def generate(self, prompt: str, **kwargs: Any) -> str:
        return f"[MOCK N-ATLaS RESPONSE] {prompt}"

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        if not messages:
            return "[MOCK N-ATLaS RESPONSE] No messages provided."

        last_message = messages[-1].get("content", "")
        return f"[MOCK N-ATLaS RESPONSE] {last_message}"

    def health(self) -> dict[str, Any]:
        return {
            "provider": "mock",
            "model": "N-ATLaS",
            "status": "healthy",
        }
