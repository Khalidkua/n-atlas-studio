from pathlib import Path

from app.services.dataset_loader import DatasetLoader


class DatasetRegistry:
    """Discover and manage evaluation datasets."""

    def __init__(self, directory: str = "datasets"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def list_datasets(self) -> list[dict]:
        datasets = []

        for path in sorted(self.directory.glob("*.jsonl")):
            try:
                dataset = DatasetLoader.load_jsonl(
                    str(path)
                )

                languages = sorted(
                    {
                        example.language
                        for example in dataset.examples
                    }
                )

                domains = sorted(
                    {
                        example.domain
                        for example in dataset.examples
                    }
                )

                task_types = sorted(
                    {
                        example.task_type
                        for example in dataset.examples
                    }
                )

                datasets.append(
                    {
                        "name": path.stem,
                        "path": str(path),
                        "format": "jsonl",
                        "examples": len(dataset.examples),
                        "languages": languages,
                        "domains": domains,
                        "task_types": task_types,
                    }
                )

            except Exception as exc:
                datasets.append(
                    {
                        "name": path.stem,
                        "path": str(path),
                        "format": "jsonl",
                        "examples": 0,
                        "languages": [],
                        "domains": [],
                        "task_types": [],
                        "error": str(exc),
                    }
                )

        return datasets

    def get_dataset(self, name: str) -> dict:
        dataset_path = self.directory / f"{name}.jsonl"

        if not dataset_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {name}"
            )

        return {
            "name": dataset_path.stem,
            "path": str(dataset_path),
            "format": "jsonl",
        }
