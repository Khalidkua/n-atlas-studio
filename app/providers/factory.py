from app.core.config import settings
from app.providers.base import NAtlasProvider
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
        )

    raise ValueError(
        f"Unsupported provider: {settings.provider}"
    )
