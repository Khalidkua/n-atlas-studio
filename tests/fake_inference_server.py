from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="N-ATLaS Fake Inference Server")


class GenerateRequest(BaseModel):
    model: str
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 512


class ChatRequest(BaseModel):
    model: str
    messages: list[dict[str, str]]
    temperature: float = 0.7
    max_tokens: int = 512


@app.post("/generate")
def generate(request: GenerateRequest):
    return {
        "response": (
            f"[FAKE N-ATLaS RESPONSE] "
            f"Model={request.model}; "
            f"Prompt={request.prompt}"
        )
    }


@app.post("/chat")
def chat(request: ChatRequest):
    last_message = (
        request.messages[-1]["content"]
        if request.messages
        else ""
    )

    return {
        "response": (
            f"[FAKE N-ATLaS CHAT RESPONSE] "
            f"Model={request.model}; "
            f"Message={last_message}"
        )
    }


@app.post("/v1/chat/completions")
def chat_completions(request: ChatRequest):
    last_message = (
        request.messages[-1]["content"]
        if request.messages
        else ""
    )

    return {
        "id": "fake-chat-completion",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": (
                        f"[FAKE N-ATLaS OPENAI CHAT] "
                        f"Model={request.model}; "
                        f"Message={last_message}"
                    ),
                },
                "finish_reason": "stop",
            }
        ],
    }


@app.post("/v1/completions")
def completions(request: GenerateRequest):
    return {
        "id": "fake-completion",
        "object": "text_completion",
        "choices": [
            {
                "index": 0,
                "text": (
                    f"[FAKE N-ATLaS OPENAI COMPLETION] "
                    f"Model={request.model}; "
                    f"Prompt={request.prompt}"
                ),
                "finish_reason": "stop",
            }
        ],
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "provider": "fake-remote",
        "model": "NCAIR1/N-ATLaS",
    }


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=9000,
    )
