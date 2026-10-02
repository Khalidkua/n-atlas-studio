from typing import Any

import requests

from .base import NAtlasProvider


class RemoteNAtlasProvider(NAtlasProvider):
    """Provider for a remotely hosted N-ATLaS inference API."""

    def __init__(
        self,
        api_url: str = "",
        api_key: str = "",
        model_name: str = "NCAIR1/N-ATLaS",
        timeout: int = 120,
        chat_url: str = "",
        generate_url: str = "",
    ):
        if not api_url and not chat_url and not generate_url:
            raise ValueError(
                "At least one remote inference URL must be configured."
            )

        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = timeout
        self.chat_url = chat_url.rstrip("/") or self.api_url
        self.generate_url = generate_url.rstrip("/") or self.api_url

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    @staticmethod
    def _extract_text(data: dict[str, Any]) -> str:
        if "response" in data:
            return str(data["response"])

        if "text" in data:
            return str(data["text"])

        if "generated_text" in data:
            return str(data["generated_text"])

        if "choices" in data and data["choices"]:
            choice = data["choices"][0]

            if "message" in choice:
                return str(choice["message"].get("content", ""))

            if "text" in choice:
                return str(choice["text"])

        raise ValueError(
            "Remote inference response format is not supported."
        )

    def generate(self, prompt: str, **kwargs: Any) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            **kwargs,
        }

        response = requests.post(
            self.generate_url,
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )

        response.raise_for_status()

        return self._extract_text(response.json())

    def chat(
        self,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> str:
        payload = {
            "model": self.model_name,
            "messages": messages,
            **kwargs,
        }

        response = requests.post(
            self.chat_url,
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )

        response.raise_for_status()

        return self._extract_text(response.json())

    def health(self) -> dict[str, Any]:
        return {
            "provider": "remote",
            "model": self.model_name,
            "status": "configured",
            "api_url": self.api_url,
            "chat_url": self.chat_url,
            "generate_url": self.generate_url,
        }
