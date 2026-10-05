import pytest

from app.services.experiment_comparator import ExperimentComparator


def test_compare_includes_response_language_accuracy():
    experiment_a = {
        "run_id": "run_a",
        "dataset": "natlas_benchmark",
        "provider": "gradio",
        "model": "NCAIR1/N-ATLaS",
        "metrics": {
            "response_language_accuracy": 0.40,
        },
    }

    experiment_b = {
        "run_id": "run_b",
        "dataset": "natlas_benchmark",
        "provider": "gradio",
        "model": "NCAIR1/N-ATLaS",
        "metrics": {
            "response_language_accuracy": 0.60,
        },
    }

    result = ExperimentComparator.compare(
        experiment_a,
        experiment_b,
    )

    language_metric = result["metrics"][
        "response_language_accuracy"
    ]

    assert language_metric["experiment_a"] == 0.40
    assert language_metric["experiment_b"] == 0.60
    assert language_metric["difference"] == pytest.approx(0.20)
