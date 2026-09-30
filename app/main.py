from fastapi import FastAPI
from pydantic import BaseModel

from app.core.config import settings
from app.providers.factory import create_provider


app = FastAPI(
    title=settings.app_name,
    description="Developer and evaluation platform for N-ATLaS",
    version=settings.app_version,
)

provider = create_provider()


class GenerateRequest(BaseModel):
    prompt: str


class ChatRequest(BaseModel):
    messages: list[dict[str, str]]


@app.get("/")
def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "provider": settings.provider,
        "model": settings.model_name,
    }


@app.get("/health")
def health():
    return provider.health()


@app.post("/generate")
def generate(request: GenerateRequest):
    return {
        "response": provider.generate(request.prompt),
        "provider": settings.provider,
        "model": settings.model_name,
    }


@app.post("/chat")
def chat(request: ChatRequest):
    return {
        "response": provider.chat(request.messages),
        "provider": settings.provider,
        "model": settings.model_name,
    }
