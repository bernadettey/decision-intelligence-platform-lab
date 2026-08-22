from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    service: str


class MetricDefinition(BaseModel):
    name: str
    description: str
    formula: str
    synonyms: list[str]
    allowed_dimensions: list[str]


class AskRequest(BaseModel):
    question: str = Field(min_length=3, examples=["Why did operating profit miss budget in March?"])


class AskResponse(BaseModel):
    answer: str
    sql_used: str
    metrics_used: list[str]
    summary_type: str = "executive_commentary"
    learning_stage: str = "fastapi_mvp"
