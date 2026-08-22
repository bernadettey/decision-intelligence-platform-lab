from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas import AskRequest, AskResponse, HealthResponse, MetricDefinition
from app.services.ai_service import AIService
from app.services.query_service import QueryService
from app.services.semantic_service import SemanticService


settings = get_settings()
app = FastAPI(title=settings.app_name)


@app.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    db.execute(text("SELECT 1"))
    return HealthResponse(status="ok", service=settings.app_name)


@app.get("/metrics", response_model=list[MetricDefinition])
def metrics() -> list[MetricDefinition]:
    return SemanticService().get_metrics()


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, db: Session = Depends(get_db)) -> AskResponse:
    semantic_service = SemanticService()
    query_service = QueryService()
    ai_service = AIService()

    metrics_used = semantic_service.infer_metrics(payload.question)
    sql_used, rows = query_service.run_variance_query(db, payload.question)
    answer = ai_service.generate_commentary(payload.question, metrics_used, rows)

    return AskResponse(
        answer=answer,
        sql_used=sql_used,
        metrics_used=metrics_used,
    )
