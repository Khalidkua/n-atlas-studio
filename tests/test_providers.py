from app.core.config import settings
from app.providers.factory import create_provider
from app.providers.mock import MockProvider
from app.providers.remote import RemoteNAtlasProvider


def test_mock_provider_factory(monkeypatch):
    monkeypatch.setattr(settings, "provider", "mock")

    provider = create_provider()

    assert isinstance(provider, MockProvider)
    assert provider.health()["status"] == "healthy"


def test_remote_provider_factory(monkeypatch):
    monkeypatch.setattr(settings, "provider", "remote")
    monkeypatch.setattr(
        settings,
        "remote_api_url",
        "http://localhost:9000/generate",
    )
    monkeypatch.setattr(
        settings,
        "remote_api_key",
        "test-key",
    )

    provider = create_provider()

    assert isinstance(provider, RemoteNAtlasProvider)
    assert provider.api_url == "http://localhost:9000/generate"
    assert provider.api_key == "test-key"
    assert provider.model_name == settings.model_name
