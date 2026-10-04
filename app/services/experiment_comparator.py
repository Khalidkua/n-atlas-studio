from typing import Any


class ExperimentComparator:
    """Compare evaluation metrics between two experiments."""

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

        token_f1_a = metrics_a.get("token_f1", 0.0)
        token_f1_b = metrics_b.get("token_f1", 0.0)

        character_similarity_a = metrics_a.get(
            "character_similarity",
            0.0,
        )
        character_similarity_b = metrics_b.get(
            "character_similarity",
            0.0,
        )

        length_a = metrics_a.get("length_ratio", 0.0)
        length_b = metrics_b.get("length_ratio", 0.0)

        return {
            "experiment_a": {
                "run_id": experiment_a.get("run_id"),
                "dataset": experiment_a.get("dataset"),
                "provider": experiment_a.get("provider"),
                "model": experiment_a.get("model"),
            },
            "experiment_b": {
                "run_id": experiment_b.get("run_id"),
                "dataset": experiment_b.get("dataset"),
                "provider": experiment_b.get("provider"),
                "model": experiment_b.get("model"),
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
                "token_f1": {
                    "experiment_a": token_f1_a,
                    "experiment_b": token_f1_b,
                    "difference": token_f1_b - token_f1_a,
                },
                "character_similarity": {
                    "experiment_a": character_similarity_a,
                    "experiment_b": character_similarity_b,
                    "difference": (
                        character_similarity_b
                        - character_similarity_a
                    ),
                },
                "length_ratio": {
                    "experiment_a": length_a,
                    "experiment_b": length_b,
                    "difference": length_b - length_a,
                },
            },
        }
