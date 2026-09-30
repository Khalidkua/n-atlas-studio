import json
from pathlib import Path

from app.models.evaluation import EvaluationDataset, EvaluationExample


REQUIRED_FIELDS = {
    "id",
    "language",
    "domain",
    "prompt",
    "reference_answer",
}


class DatasetLoader:
    """Load and validate N-ATLAS Studio evaluation datasets."""

    @staticmethod
    def load_jsonl(path: str) -> EvaluationDataset:
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {file_path}"
            )

        examples: list[EvaluationExample] = []

        with file_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue

                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON on line {line_number}: {exc}"
                    ) from exc

                missing_fields = REQUIRED_FIELDS - record.keys()

                if missing_fields:
                    raise ValueError(
                        f"Missing fields on line {line_number}: "
                        f"{sorted(missing_fields)}"
                    )

                examples.append(
                    EvaluationExample(**record)
                )

        return EvaluationDataset(
            name=file_path.stem,
            examples=examples,
        )
