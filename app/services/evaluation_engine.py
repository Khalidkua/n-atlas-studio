from collections import defaultdict
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

    def evaluate(
        self,
        dataset: EvaluationDataset,
        temperature: float = 0.7,
        max_tokens: int = 512,
        languages: list[str] | None = None,
        task_types: list[str] | None = None,
    ) -> dict[str, Any]:

        languages = languages or []
        task_types = task_types or []

        filtered_examples = [
            example
            for example in dataset.examples
            if (
                not languages
                or example.language in languages
            )
            and (
                not task_types
                or example.task_type in task_types
            )
        ]

        results = []

        exact_match_total = 0.0
        word_overlap_total = 0.0

        language_metrics = defaultdict(
            lambda: {
                "examples": 0,
                "exact_match_total": 0.0,
                "word_overlap_total": 0.0,
            }
        )

        domain_metrics = defaultdict(
            lambda: {
                "examples": 0,
                "exact_match_total": 0.0,
                "word_overlap_total": 0.0,
            }
        )

        task_metrics = defaultdict(
            lambda: {
                "examples": 0,
                "exact_match_total": 0.0,
                "word_overlap_total": 0.0,
            }
        )

        for example in filtered_examples:

            generated_answer = self.provider.generate(
                example.prompt,
                temperature=temperature,
                max_tokens=max_tokens,
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

            # -----------------------------------------
            # Language metrics
            # -----------------------------------------

            language = example.language

            language_metrics[language]["examples"] += 1

            language_metrics[language][
                "exact_match_total"
            ] += exact_match

            language_metrics[language][
                "word_overlap_total"
            ] += word_overlap

            # -----------------------------------------
            # Domain metrics
            # -----------------------------------------

            domain = example.domain

            domain_metrics[domain]["examples"] += 1

            domain_metrics[domain][
                "exact_match_total"
            ] += exact_match

            domain_metrics[domain][
                "word_overlap_total"
            ] += word_overlap

            # -----------------------------------------
            # Task type metrics
            # -----------------------------------------

            task_type = example.task_type

            task_metrics[task_type]["examples"] += 1

            task_metrics[task_type][
                "exact_match_total"
            ] += exact_match

            task_metrics[task_type][
                "word_overlap_total"
            ] += word_overlap

            # -----------------------------------------
            # Individual result
            # -----------------------------------------

            results.append(
                {
                    "id": example.id,
                    "language": example.language,
                    "domain": example.domain,
                    "task_type": example.task_type,
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

        # -----------------------------------------
        # Final language metrics
        # -----------------------------------------

        by_language = {}

        for language, metrics in language_metrics.items():

            count = metrics["examples"]

            by_language[language] = {
                "examples": count,
                "exact_match": (
                    metrics["exact_match_total"] / count
                    if count
                    else 0.0
                ),
                "word_overlap": (
                    metrics["word_overlap_total"] / count
                    if count
                    else 0.0
                ),
            }

        # -----------------------------------------
        # Final task type metrics
        # -----------------------------------------

        by_task_type = {}

        for task_type, metrics in task_metrics.items():

            count = metrics["examples"]

            by_task_type[task_type] = {
                "examples": count,
                "exact_match": (
                    metrics["exact_match_total"] / count
                    if count
                    else 0.0
                ),
                "word_overlap": (
                    metrics["word_overlap_total"] / count
                    if count
                    else 0.0
                ),
            }

        # -----------------------------------------
        # Final domain metrics
        # -----------------------------------------

        by_domain = {}

        for domain, metrics in domain_metrics.items():

            count = metrics["examples"]

            by_domain[domain] = {
                "examples": count,
                "exact_match": (
                    metrics["exact_match_total"] / count
                    if count
                    else 0.0
                ),
                "word_overlap": (
                    metrics["word_overlap_total"] / count
                    if count
                    else 0.0
                ),
            }

        return {
            "dataset": dataset.name,
            "total_examples": total,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "languages": languages,
            "task_types": task_types,
            "metrics": {
                "exact_match": average_exact_match,
                "word_overlap": average_word_overlap,
            },
            "by_language": by_language,
            "by_task_type": by_task_type,
            "by_domain": by_domain,
            "results": results,
        }
