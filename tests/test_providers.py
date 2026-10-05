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

def test_gradio_provider_factory_passes_model_configuration(monkeypatch):
    monkeypatch.setattr(settings, "provider", "gradio")
    monkeypatch.setattr(
        settings,
        "gradio_space",
        "test-space",
    )
    monkeypatch.setattr(
        settings,
        "gradio_model_key",
        "N-ATLaS-LLM",
    )
    monkeypatch.setattr(
        settings,
        "model_name",
        "NCAIR1/N-ATLaS",
    )

    captured = {}

    class FakeGradioProvider:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr(
        "app.providers.factory.GradioNAtlasProvider",
        FakeGradioProvider,
    )

    provider = create_provider()

    assert isinstance(provider, FakeGradioProvider)
    assert captured["space"] == "test-space"
    assert captured["model_key"] == "N-ATLaS-LLM"
    assert captured["model_name"] == "NCAIR1/N-ATLaS"

