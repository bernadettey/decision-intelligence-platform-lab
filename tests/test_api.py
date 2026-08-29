from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.config import get_settings
from app.database import SessionLocal, get_db
from app.main import app, get_ai_service, get_query_service


@pytest.fixture(autouse=True)
def clear_dependency_overrides() -> Generator[None, None, None]:
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_health_success() -> None:
    session = SessionLocal()
    try:
        try:
            session.execute(text("SELECT 1"))
            session.rollback()
        except SQLAlchemyError as exc:
            pytest.skip(f"PostgreSQL test database is unavailable: {exc}")
    finally:
        session.close()

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Decision Intelligence Platform Lab",
    }


def test_health_database_operational_failure_returns_503() -> None:
    class FailingDb:
        def execute(self, statement):
            raise OperationalError(str(statement), {}, Exception("database unavailable"))

    def override_get_db():
        yield FailingDb()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}


def test_metrics_returns_current_semantic_metrics() -> None:
    client = TestClient(app)

    response = client.get("/metrics")

    assert response.status_code == 200
    payload = response.json()
    metric_names = {row["name"] for row in payload}
    assert "operating_profit" in metric_names
    assert "budget_variance" in metric_names


def test_ask_deterministic_success_with_dependency_overrides() -> None:
    class FakeQueryService:
        def run_saas_commercial_summary(self, db):
            return (
                "SELECT * FROM operations.subscriptions",
                [
                    {
                        "business_unit": "SaaS",
                        "region": "APAC",
                        "active_subscriptions": 2,
                        "subscription_events": 2,
                        "arr_amount": Decimal("120000.00"),
                        "mrr_amount": Decimal("10000.00"),
                    }
                ],
            )

    class FakeAIService:
        def generate_commentary(self, question, metrics_used, rows):
            return "Deterministic API commentary."

    app.dependency_overrides[get_query_service] = lambda: FakeQueryService()
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService()
    client = TestClient(app)

    response = client.post("/ask", json={"question": "What is SaaS ARR?"})

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Deterministic API commentary.",
        "sql_used": "SELECT * FROM operations.subscriptions",
        "metrics_used": ["operating_profit", "budget_variance"],
        "summary_type": "executive_commentary",
        "learning_stage": "m1_backend",
    }


def test_ask_rejects_too_short_question() -> None:
    client = TestClient(app)

    response = client.post("/ask", json={"question": "no"})

    assert response.status_code == 422


def test_ask_database_operational_failure_returns_503() -> None:
    class FailingQueryService:
        def run_saas_commercial_summary(self, db):
            raise OperationalError("SELECT 1", {}, Exception("database unavailable"))

    app.dependency_overrides[get_query_service] = lambda: FailingQueryService()
    client = TestClient(app)

    response = client.post("/ask", json={"question": "What is SaaS ARR?"})

    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}


def test_ask_real_postgres_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    session = SessionLocal()
    try:
        try:
            session.execute(text("SELECT 1"))
            session.rollback()
        except SQLAlchemyError as exc:
            pytest.skip(f"PostgreSQL test database is unavailable: {exc}")
    finally:
        session.close()

    monkeypatch.setattr(get_settings(), "openai_api_key", None)
    client = TestClient(app)

    response = client.post("/ask", json={"question": "What is SaaS ARR?"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["learning_stage"] == "m1_backend"
    assert "operations.subscriptions" in payload["sql_used"]
    assert payload["summary_type"] == "executive_commentary"
