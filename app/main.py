from fastapi import FastAPI
from pydantic import BaseModel
from app.services.experiment_store import ExperimentStore

from app.core.config import settings
from app.providers.factory import create_provider
from app.services.dataset_loader import DatasetLoader
from app.services.evaluation_engine import EvaluationEngine


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


class EvaluateRequest(BaseModel):
    dataset_path: str


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


@app.post("/evaluate")
def evaluate(request: EvaluateRequest):
    dataset = DatasetLoader.load_jsonl(
        request.dataset_path
    )

    engine = EvaluationEngine(provider)

    report = engine.evaluate(dataset)

    store = ExperimentStore()

    return store.save(report)
