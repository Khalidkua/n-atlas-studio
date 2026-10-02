from app.models.evaluation import EvaluationDataset, EvaluationExample
from app.services.evaluation_engine import EvaluationEngine


class RecordingProvider:
    def __init__(self):
        self.calls = []

    def generate(self, prompt: str, **kwargs):
        self.calls.append(
            {
                "prompt": prompt,
                "kwargs": kwargs,
            }
        )
        return "test response"


def test_evaluation_passes_generation_configuration():
    provider = RecordingProvider()
    engine = EvaluationEngine(provider)

    dataset = EvaluationDataset(
        name="test_dataset",
        examples=[
            EvaluationExample(
                id="test_001",
                language="English",
                domain="computer_science",
                task_type="question_answering",
                prompt="What is Python?",
                reference_answer="test response",
            )
        ],
    )

    report = engine.evaluate(
        dataset,
        temperature=0.3,
        max_tokens=256,
    )

    assert len(provider.calls) == 1

    assert provider.calls[0]["kwargs"]["temperature"] == 0.3
    assert provider.calls[0]["kwargs"]["max_tokens"] == 256

    assert report["temperature"] == 0.3
    assert report["max_tokens"] == 256