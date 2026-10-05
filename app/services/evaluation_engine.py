from collections import defaultdict
import re
from typing import Any

from app.models.evaluation import EvaluationDataset
from app.providers.base import NAtlasProvider
from app.services.language_detector import LanguageDetector
from app.services.metrics import (
    exact_match_score,
    word_overlap_score,
    token_f1_score,
    character_similarity_score,
    word_count,
    length_ratio,
)


class EvaluationEngine:
    """Run an evaluation dataset through an N-ATLaS provider."""

    def __init__(self, provider: NAtlasProvider):
        self.provider = provider
        self.language_detector = LanguageDetector()

    @staticmethod
    def _expected_response_language(example: Any) -> str:
        """Determine the language expected in the generated response."""

        if example.task_type == "translation":
            match = re.search(
                r"Translate to (Hausa|English|Igbo|Yoruba):",
                example.prompt,
                re.IGNORECASE,
            )

            if match:
                return match.group(1).capitalize()

        return example.language

    @staticmethod
    def _create_metric_bucket() -> dict[str, float | int]:
        return {
            "examples": 0,
            "exact_match_total": 0.0,
            "word_overlap_total": 0.0,
            "token_f1_total": 0.0,
            "character_similarity_total": 0.0,
            "length_ratio_total": 0.0,
            "language_known_examples": 0,
            "language_match_total": 0.0,
        }

    @staticmethod
    def _finalize_metrics(
        metrics: dict[str, float | int],
    ) -> dict[str, float | int]:
        count = int(metrics["examples"])
        language_known = int(metrics["language_known_examples"])

        return {
            "examples": count,
            "exact_match": (
                float(metrics["exact_match_total"]) / count
                if count
                else 0.0
            ),
            "word_overlap": (
                float(metrics["word_overlap_total"]) / count
                if count
                else 0.0
            ),
            "token_f1": (
                float(metrics["token_f1_total"]) / count
                if count
                else 0.0
            ),
            "character_similarity": (
                float(metrics["character_similarity_total"])
                / count
                if count
                else 0.0
            ),
            "length_ratio": (
                float(metrics["length_ratio_total"]) / count
                if count
                else 0.0
            ),
            "language_known_examples": language_known,
            "response_language_accuracy": (
                float(metrics["language_match_total"])
                / language_known
                if language_known
                else 0.0
            ),
        }

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
        token_f1_total = 0.0
        character_similarity_total = 0.0
        length_ratio_total = 0.0

        language_known_total = 0
        language_match_total = 0.0

        language_metrics = defaultdict(
            self._create_metric_bucket
        )

        domain_metrics = defaultdict(
            self._create_metric_bucket
        )

        task_metrics = defaultdict(
            self._create_metric_bucket
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

            token_f1 = token_f1_score(
                generated_answer,
                example.reference_answer,
            )

            character_similarity = character_similarity_score(
                generated_answer,
                example.reference_answer,
            )

            generated_word_count = word_count(
                generated_answer
            )

            reference_word_count = word_count(
                example.reference_answer
            )

            answer_length_ratio = length_ratio(
                generated_answer,
                example.reference_answer,
            )

            # -----------------------------------------
            # Response-language evaluation
            # -----------------------------------------

            expected_response_language = (
                self._expected_response_language(example)
            )

            language_detection = self.language_detector.detect(
                generated_answer
            )

            detected_language = language_detection["language"]
            language_detection_confidence = (
                language_detection["confidence"]
            )

            language_match = (
                detected_language != "unknown"
                and detected_language.lower()
                == expected_response_language.lower()
            )

            language_is_known = detected_language != "unknown"

            # -----------------------------------------
            # Overall metrics
            # -----------------------------------------

            exact_match_total += exact_match
            word_overlap_total += word_overlap
            token_f1_total += token_f1
            character_similarity_total += character_similarity
            length_ratio_total += answer_length_ratio

            if language_is_known:
                language_known_total += 1

                if language_match:
                    language_match_total += 1

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

            language_metrics[language][
                "token_f1_total"
            ] += token_f1

            language_metrics[language][
                "character_similarity_total"
            ] += character_similarity

            language_metrics[language][
                "length_ratio_total"
            ] += answer_length_ratio

            if language_is_known:
                language_metrics[language][
                    "language_known_examples"
                ] += 1

                if language_match:
                    language_metrics[language][
                        "language_match_total"
                    ] += 1

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

            domain_metrics[domain][
                "token_f1_total"
            ] += token_f1

            domain_metrics[domain][
                "character_similarity_total"
            ] += character_similarity

            domain_metrics[domain][
                "length_ratio_total"
            ] += answer_length_ratio

            if language_is_known:
                domain_metrics[domain][
                    "language_known_examples"
                ] += 1

                if language_match:
                    domain_metrics[domain][
                        "language_match_total"
                    ] += 1

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

            task_metrics[task_type][
                "token_f1_total"
            ] += token_f1

            task_metrics[task_type][
                "character_similarity_total"
            ] += character_similarity

            task_metrics[task_type][
                "length_ratio_total"
            ] += answer_length_ratio

            if language_is_known:
                task_metrics[task_type][
                    "language_known_examples"
                ] += 1

                if language_match:
                    task_metrics[task_type][
                        "language_match_total"
                    ] += 1

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
                    "expected_response_language": (
                        expected_response_language
                    ),
                    "detected_language": detected_language,
                    "language_match": language_match,
                    "language_detection_confidence": (
                        language_detection_confidence
                    ),
                    "metrics": {
                        "exact_match": exact_match,
                        "word_overlap": word_overlap,
                        "token_f1": token_f1,
                        "character_similarity": character_similarity,
                        "generated_word_count": generated_word_count,
                        "reference_word_count": reference_word_count,
                        "length_ratio": answer_length_ratio,
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

            average_token_f1 = (
                token_f1_total / total
            )

            average_character_similarity = (
                character_similarity_total / total
            )

            average_length_ratio = (
                length_ratio_total / total
            )

        else:
            average_exact_match = 0.0
            average_word_overlap = 0.0
            average_token_f1 = 0.0
            average_character_similarity = 0.0
            average_length_ratio = 0.0

        # -----------------------------------------
        # Final language metrics
        # -----------------------------------------

        by_language = {
            language: self._finalize_metrics(metrics)
            for language, metrics in language_metrics.items()
        }

        # -----------------------------------------
        # Final task type metrics
        # -----------------------------------------

        by_task_type = {
            task_type: self._finalize_metrics(metrics)
            for task_type, metrics in task_metrics.items()
        }

        # -----------------------------------------
        # Final domain metrics
        # -----------------------------------------

        by_domain = {
            domain: self._finalize_metrics(metrics)
            for domain, metrics in domain_metrics.items()
        }

        response_language_accuracy = (
            language_match_total / language_known_total
            if language_known_total
            else 0.0
        )

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
                "token_f1": average_token_f1,
                "character_similarity": average_character_similarity,
                "length_ratio": average_length_ratio,
                "response_language_accuracy": (
                    response_language_accuracy
                ),
                "language_known_examples": language_known_total,
            },
            "by_language": by_language,
            "by_task_type": by_task_type,
            "by_domain": by_domain,
            "results": results,
        }
