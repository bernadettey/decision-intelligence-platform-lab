from app.services.semantic_service import SemanticService


def test_infer_budget_variance_metrics() -> None:
    service = SemanticService()

    metrics = service.infer_metrics("Why did operating profit miss budget in March?")

    assert "operating_profit" in metrics
    assert "budget_variance" in metrics
