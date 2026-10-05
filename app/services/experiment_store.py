import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.core.config import settings


class ExperimentStore:
    """Persist evaluation runs as JSON files."""

    def __init__(self, directory: str = "experiments"):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, report: dict) -> dict:
        run_id = str(uuid4())

        experiment = {
            "run_id": run_id,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "provider": settings.provider,
            "model": settings.model_name,
            **report,
        }

        file_path = self.directory / f"{run_id}.json"

        with file_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                experiment,
                file,
                indent=2,
                ensure_ascii=False,
            )

        return experiment

    def list(self) -> list[dict]:
        """Return saved experiments, newest first."""

        experiments = []

        for path in sorted(
            self.directory.glob("*.json"),
            key=lambda item: item.stat().st_mtime,
            reverse=True,
        ):
            try:
                with path.open(
                    "r",
                    encoding="utf-8",
                ) as file:
                    experiments.append(
                        json.load(file)
                    )
            except (OSError, json.JSONDecodeError):
                continue

        return experiments

    def get(self, run_id: str) -> dict | None:
        """Return a saved experiment by run ID."""

        file_path = self.directory / f"{run_id}.json"

        if not file_path.exists():
            return None

        try:
            with file_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            return None
