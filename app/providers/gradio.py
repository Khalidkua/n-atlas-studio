from typing import Any

from gradio_client import Client

from .base import NAtlasProvider


class GradioNAtlasProvider(NAtlasProvider):
    """Provider for N-ATLaS served through a Gradio Space."""

    def __init__(
        self,
        space: str = "seun-ajayi/n-atlas-evaluations",
        model_key: str = "N-ATLaS-LLM",
    ):
        self.space = space
        self.model_key = model_key
        self.client = Client(space)

    def generate(self, prompt: str, **kwargs: Any) -> str:
        return self.chat(
            [{"role": "user", "content": prompt}],
            **kwargs,
        )

    def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        if not messages:
            raise ValueError("At least one chat message is required.")

        # The public Space currently accepts a plain text message.
        prompt = messages[-1].get("content", "")

        result = self.client.predict(
            prompt,
            self.model_key,
            api_name="/chat",
        )

        if isinstance(result, dict):
            if "response" in result:
                return str(result["response"])
            if "text" in result:
                return str(result["text"])

        return str(result)

    def health(self) -> dict[str, Any]:
        return {
            "provider": "gradio",
            "model": self.model_key,
            "status": "configured",
            "space": self.space,
        }
