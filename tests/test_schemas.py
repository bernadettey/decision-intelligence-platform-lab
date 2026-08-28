from app.schemas import AskResponse


def test_ask_response_includes_current_learning_stage() -> None:
    response = AskResponse(
        answer="Operating profit was below budget.",
        sql_used="SELECT 1",
        metrics_used=["operating_profit", "budget_variance"],
    )

    assert response.learning_stage == "m1_backend"
