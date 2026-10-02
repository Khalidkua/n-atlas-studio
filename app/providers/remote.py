from typing import Any

import requests

from .base import NAtlasProvider


class RemoteNAtlasProvider(NAtlasProvider):
    """Provider for a remotely hosted N-ATLaS inference API."""

    def __init__(
        self,
        api_url: str,
        api_key: str = "",
        model_name: str = "NCAIR1/N-ATLaS",
        timeout: int = 120,
    ):
        if not api_url:
            raise ValueError(
                "REMOTE_API_URL must be configured for the remote provider."
            )

        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    def generate(self, prompt: str, **kwargs: Any) -> str:
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            **kwargs,
        }

        response = requests.post(
            self.api_url,
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        if "response" in data:
            return str(data["response"])

        if "text" in data:
            return str(data["text"])

        if "generated_text" in data:
            return str(data["generated_text"])

        raise ValueError(
            "Remote inference response does not contain "
            "'response', 'text', or 'generated_text'."
        )

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
            self.api_url,
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

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
            "Remote chat response format is not supported."
        )

    def health(self) -> dict[str, Any]:
        return {
            "provider": "remote",
            "model": self.model_name,
            "status": "configured",
            "api_url": self.api_url,
        }
