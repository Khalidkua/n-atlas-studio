import json

from app.services.experiment_store import ExperimentStore


def test_list_returns_experiments_newest_first(tmp_path):
    store = ExperimentStore(
        directory=str(tmp_path)
    )

    first = {
        "run_id": "run_a",
        "timestamp": "2026-10-01T10:00:00+00:00",
        "metrics": {"exact_match": 0.1},
    }

    second = {
        "run_id": "run_b",
        "timestamp": "2026-10-02T10:00:00+00:00",
        "metrics": {"exact_match": 0.2},
    }

    (tmp_path / "run_a.json").write_text(
        json.dumps(first),
        encoding="utf-8",
    )

    (tmp_path / "run_b.json").write_text(
        json.dumps(second),
        encoding="utf-8",
    )

    experiments = store.list()

    assert len(experiments) == 2
    assert experiments[0]["run_id"] == "run_b"
    assert experiments[1]["run_id"] == "run_a"


def test_get_returns_experiment_by_run_id(tmp_path):
    store = ExperimentStore(
        directory=str(tmp_path)
    )

    experiment = {
        "run_id": "run_a",
        "metrics": {
            "response_language_accuracy": 0.75,
        },
    }

    (tmp_path / "run_a.json").write_text(
        json.dumps(experiment),
        encoding="utf-8",
    )

    result = store.get("run_a")

    assert result == experiment


def test_get_returns_none_for_missing_experiment(tmp_path):
    store = ExperimentStore(
        directory=str(tmp_path)
    )

    assert store.get("missing-run") is None
