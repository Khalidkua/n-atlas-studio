from typing import Any


class ExperimentComparator:
    """Compare metrics from two evaluation runs."""

    @staticmethod
    def compare(
        experiment_a: dict[str, Any],
        experiment_b: dict[str, Any],
    ) -> dict[str, Any]:

        metrics_a = experiment_a.get("metrics", {})
        metrics_b = experiment_b.get("metrics", {})

        exact_a = metrics_a.get("exact_match", 0.0)
        exact_b = metrics_b.get("exact_match", 0.0)

        overlap_a = metrics_a.get("word_overlap", 0.0)
        overlap_b = metrics_b.get("word_overlap", 0.0)

        length_a = metrics_a.get("length_ratio", 0.0)
        length_b = metrics_b.get("length_ratio", 0.0)

        return {
            "experiment_a": {
                "run_id": experiment_a.get("run_id"),
                "dataset": experiment_a.get("dataset"),
                "provider": experiment_a.get("provider"),
                "model": experiment_a.get("model"),
                "temperature": experiment_a.get("temperature", 0.7),
                "max_tokens": experiment_a.get("max_tokens", 512),
                "languages": experiment_a.get("languages", []),
                "task_types": experiment_a.get("task_types", []),
            },
            "experiment_b": {
                "run_id": experiment_b.get("run_id"),
                "dataset": experiment_b.get("dataset"),
                "provider": experiment_b.get("provider"),
                "model": experiment_b.get("model"),
                "temperature": experiment_b.get("temperature", 0.7),
                "max_tokens": experiment_b.get("max_tokens", 512),
                "languages": experiment_b.get("languages", []),
                "task_types": experiment_b.get("task_types", []),
            },
            "metrics": {
                "exact_match": {
                    "experiment_a": exact_a,
                    "experiment_b": exact_b,
                    "difference": exact_b - exact_a,
                },
                "word_overlap": {
                    "experiment_a": overlap_a,
                    "experiment_b": overlap_b,
                    "difference": overlap_b - overlap_a,
                },
                "length_ratio": {
                    "experiment_a": length_a,
                    "experiment_b": length_b,
                    "difference": length_b - length_a,
                },
            },
        }
