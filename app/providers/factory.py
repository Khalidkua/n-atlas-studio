from app.core.config import settings
from app.providers.base import NAtlasProvider
from app.providers.gradio import GradioNAtlasProvider
from app.providers.mock import MockProvider
from app.providers.remote import RemoteNAtlasProvider


def create_provider() -> NAtlasProvider:
    """Create the configured N-ATLaS provider."""

    provider_name = settings.provider.lower()

    if provider_name == "mock":
        return MockProvider()

    if provider_name == "remote":
        return RemoteNAtlasProvider(
            api_url=settings.remote_api_url,
            api_key=settings.remote_api_key,
            model_name=settings.model_name,
            chat_url=settings.remote_chat_url,
            generate_url=settings.remote_generate_url,
        )

    if provider_name == "gradio":
        return GradioNAtlasProvider(
            space=settings.gradio_space,
            model_key=settings.gradio_model_key,
        )

    raise ValueError(
        f"Unsupported provider: {settings.provider}"
    )
