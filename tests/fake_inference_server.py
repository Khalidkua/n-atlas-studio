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
