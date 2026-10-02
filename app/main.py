from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.services.dataset_registry import DatasetRegistry
from app.providers.factory import create_provider
from app.services.dataset_loader import DatasetLoader
from app.services.evaluation_engine import EvaluationEngine
from app.services.experiment_comparator import ExperimentComparator
from app.services.experiment_store import ExperimentStore


app = FastAPI(
    title=settings.app_name,
    description="Developer and evaluation platform for N-ATLaS",
    version=settings.app_version,
)

provider = create_provider()


class GenerateRequest(BaseModel):
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 512


class ChatRequest(BaseModel):
    messages: list[dict[str, str]]


class EvaluateRequest(BaseModel):
    dataset_path: str
    temperature: float = 0.7
    max_tokens: int = 512

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
        "response": provider.generate(
            request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        ),
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


@app.get("/datasets")
def list_datasets():
    registry = DatasetRegistry()

    return {
        "datasets": registry.list_datasets()
    }


@app.post("/evaluate")
def evaluate(request: EvaluateRequest):
    dataset = DatasetLoader.load_jsonl(
        request.dataset_path
    )

    engine = EvaluationEngine(provider)

    report = engine.evaluate(
    dataset,
    temperature=request.temperature,
    max_tokens=request.max_tokens,
)

    store = ExperimentStore()

    return store.save(report)


@app.post("/experiments/compare")
def compare_experiments(
    run_id_a: str,
    run_id_b: str,
):
    store = ExperimentStore()

    experiment_a_path = (
        store.directory / f"{run_id_a}.json"
    )

    experiment_b_path = (
        store.directory / f"{run_id_b}.json"
    )

    if not experiment_a_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Experiment not found: {run_id_a}",
        )

    if not experiment_b_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Experiment not found: {run_id_b}",
        )

    import json

    with experiment_a_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        experiment_a = json.load(file)

    with experiment_b_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        experiment_b = json.load(file)

    return ExperimentComparator.compare(
        experiment_a,
        experiment_b,
    )
