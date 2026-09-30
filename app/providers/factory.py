from app.core.config import settings
from app.providers.base import NAtlasProvider
from app.providers.mock import MockProvider


def create_provider() -> NAtlasProvider:
    """Create the configured N-ATLaS provider."""

    provider_name = settings.provider.lower()

    if provider_name == "mock":
        return MockProvider()

    raise ValueError(
        f"Unsupported provider: {settings.provider}"
    )
