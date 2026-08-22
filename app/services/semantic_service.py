from pathlib import Path

import yaml

from app.config import get_settings
from app.schemas import MetricDefinition


class SemanticService:
    def __init__(self, metrics_path: str | None = None) -> None:
        settings = get_settings()
        self.metrics_path = Path(metrics_path or settings.semantic_metrics_path)

    def get_metrics(self) -> list[MetricDefinition]:
        with self.metrics_path.open("r", encoding="utf-8") as file:
            payload = yaml.safe_load(file) or {}

        metrics = payload.get("metrics", {})
        return [
            MetricDefinition(name=name, **definition)
            for name, definition in metrics.items()
        ]

    def infer_metrics(self, question: str) -> list[str]:
        normalized = question.lower()
        matched: list[str] = []

        for metric in self.get_metrics():
            terms = [metric.name, *metric.synonyms]
            if any(term.replace("_", " ").lower() in normalized for term in terms):
                matched.append(metric.name)

        if "budget" in normalized and "budget_variance" not in matched:
            matched.append("budget_variance")
        if "forecast" in normalized and "forecast_variance" not in matched:
            matched.append("forecast_variance")

        return matched or ["operating_profit", "budget_variance"]
