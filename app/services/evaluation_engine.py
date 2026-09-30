from typing import Any

from app.models.evaluation import EvaluationDataset
from app.providers.base import NAtlasProvider
from app.services.metrics import (
    exact_match_score,
    word_overlap_score,
)


class EvaluationEngine:
    """Run an evaluation dataset through an N-ATLaS provider."""

    def __init__(self, provider: NAtlasProvider):
        self.provider = provider

    def evaluate(self, dataset: EvaluationDataset) -> dict[str, Any]:
        results = []

        exact_match_total = 0.0
        word_overlap_total = 0.0

        for example in dataset.examples:
            generated_answer = self.provider.generate(
                example.prompt
            )

            exact_match = exact_match_score(
                generated_answer,
                example.reference_answer,
            )

            word_overlap = word_overlap_score(
                generated_answer,
                example.reference_answer,
            )

            exact_match_total += exact_match
            word_overlap_total += word_overlap

            results.append(
                {
                    "id": example.id,
                    "language": example.language,
                    "domain": example.domain,
                    "prompt": example.prompt,
                    "reference_answer": example.reference_answer,
                    "generated_answer": generated_answer,
                    "metrics": {
                        "exact_match": exact_match,
                        "word_overlap": word_overlap,
                    },
                }
            )

        total = len(results)

        if total > 0:
            average_exact_match = (
                exact_match_total / total
            )

            average_word_overlap = (
                word_overlap_total / total
            )
        else:
            average_exact_match = 0.0
            average_word_overlap = 0.0

        return {
            "dataset": dataset.name,
            "total_examples": total,
            "metrics": {
                "exact_match": average_exact_match,
                "word_overlap": average_word_overlap,
            },
            "results": results,
        }
