from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas import AskRequest, AskResponse, HealthResponse, MetricDefinition
from app.services.ai_service import AIService
from app.services.query_service import QueryService
from app.services.semantic_service import SemanticService


settings = get_settings()
app = FastAPI(title=settings.app_name)


def get_query_service() -> QueryService:
    return QueryService()


def get_ai_service() -> AIService:
    return AIService()


@app.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    try:
        db.execute(text("SELECT 1"))
    except OperationalError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return HealthResponse(status="ok", service=settings.app_name)


@app.get("/metrics", response_model=list[MetricDefinition])
def metrics() -> list[MetricDefinition]:
    return SemanticService().get_metrics()


@app.post("/ask", response_model=AskResponse)
def ask(
    payload: AskRequest,
    db: Session = Depends(get_db),
    query_service: QueryService = Depends(get_query_service),
    ai_service: AIService = Depends(get_ai_service),
) -> AskResponse:
    semantic_service = SemanticService()

    metrics_used = semantic_service.infer_metrics(payload.question)
    try:
        sql_used, rows = query_service.run_saas_commercial_summary(db)
    except OperationalError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    answer = ai_service.generate_commentary(payload.question, metrics_used, rows)

    return AskResponse(
        answer=answer,
        sql_used=sql_used,
        metrics_used=metrics_used,
    )
