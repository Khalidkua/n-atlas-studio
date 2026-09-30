from fastapi import FastAPI
from pydantic import BaseModel

from app.providers.mock import MockProvider


app = FastAPI(
    title="N-ATLAS Studio",
    description="Developer and evaluation platform for N-ATLaS",
    version="0.1.0",
)

provider = MockProvider()


class GenerateRequest(BaseModel):
    prompt: str


class ChatRequest(BaseModel):
    messages: list[dict[str, str]]


@app.get("/")
def root():
    return {
        "name": "N-ATLAS Studio",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return provider.health()


@app.post("/generate")
def generate(request: GenerateRequest):
    return {
        "response": provider.generate(request.prompt),
        "provider": "mock",
    }


@app.post("/chat")
def chat(request: ChatRequest):
    return {
        "response": provider.chat(request.messages),
        "provider": "mock",
    }
