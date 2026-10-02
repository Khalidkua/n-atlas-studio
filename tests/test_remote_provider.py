from app.providers.remote import RemoteNAtlasProvider


class FakeResponse:
    def __init__(self, data):
        self._data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._data


def test_remote_generate(monkeypatch):
    provider = RemoteNAtlasProvider(
        api_url="http://localhost:9000/generate",
        api_key="test-key",
        model_name="NCAIR1/N-ATLaS",
    )

    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        captured["timeout"] = timeout

        return FakeResponse(
            {
                "response": "Test N-ATLaS response",
            }
        )

    monkeypatch.setattr(
        "app.providers.remote.requests.post",
        fake_post,
    )

    result = provider.generate(
        "Hello N-ATLaS",
        temperature=0.5,
        max_tokens=100,
    )

    assert result == "Test N-ATLaS response"
    assert captured["url"] == "http://localhost:9000/generate"
    assert captured["json"]["model"] == "NCAIR1/N-ATLaS"
    assert captured["json"]["prompt"] == "Hello N-ATLaS"
    assert captured["json"]["temperature"] == 0.5
    assert captured["json"]["max_tokens"] == 100
    assert captured["headers"]["Authorization"] == "Bearer test-key"


def test_remote_chat(monkeypatch):
    provider = RemoteNAtlasProvider(
        api_url="http://localhost:9000/chat",
        model_name="NCAIR1/N-ATLaS",
    )

    def fake_post(url, json, headers, timeout):
        return FakeResponse(
            {
                "response": "Test chat response",
            }
        )

    monkeypatch.setattr(
        "app.providers.remote.requests.post",
        fake_post,
    )

    result = provider.chat(
        [
            {
                "role": "user",
                "content": "Hello",
            }
        ]
    )

    assert result == "Test chat response"


def test_remote_chat_openai_compatible(monkeypatch):
    provider = RemoteNAtlasProvider(
        chat_url="http://localhost:9000/v1/chat/completions",
        model_name="NCAIR1/N-ATLaS",
    )

    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json

        return FakeResponse(
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": "OpenAI-compatible response",
                        }
                    }
                ]
            }
        )

    monkeypatch.setattr(
        "app.providers.remote.requests.post",
        fake_post,
    )

    result = provider.chat(
        [
            {
                "role": "user",
                "content": "Hello N-ATLaS",
            }
        ],
        temperature=0.3,
        max_tokens=128,
    )

    assert result == "OpenAI-compatible response"
    assert captured["url"] == "http://localhost:9000/v1/chat/completions"
    assert captured["json"]["model"] == "NCAIR1/N-ATLaS"
    assert captured["json"]["temperature"] == 0.3
    assert captured["json"]["max_tokens"] == 128


def test_remote_generate_openai_compatible(monkeypatch):
    provider = RemoteNAtlasProvider(
        generate_url="http://localhost:9000/v1/completions",
        model_name="NCAIR1/N-ATLaS",
    )

    def fake_post(url, json, headers, timeout):
        return FakeResponse(
            {
                "choices": [
                    {
                        "text": "OpenAI-compatible completion",
                    }
                ]
            }
        )

    monkeypatch.setattr(
        "app.providers.remote.requests.post",
        fake_post,
    )

    result = provider.generate(
        "Explain databases.",
        temperature=0.2,
        max_tokens=64,
    )

    assert result == "OpenAI-compatible completion"
