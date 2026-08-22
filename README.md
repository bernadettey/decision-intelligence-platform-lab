# Decision Intelligence Platform

Decision Intelligence Platform is a GitHub-ready AI engineering project for governed, tool-using, evaluated business decision workflows.

The first use case is FP&A variance analysis and executive commentary. It simulates how a Finance / FP&A team reviews monthly Budget vs Actual, Forecast vs Actual, Variance Analysis, Margin Analysis, and Executive Commentary.

## Business Problem

FP&A teams spend significant time reconciling actuals against budgets and forecasts, identifying margin drivers, and turning financial data into executive-ready commentary. This work is often manual, repetitive, and spread across spreadsheets, BI dashboards, and finance systems.

## Solution

This MVP provides a small AI-powered decision workflow:

- Store synthetic actuals, budgets, forecasts, business units, and cost centres in PostgreSQL.
- Define finance metrics in a YAML semantic layer.
- Ask natural-language FP&A questions through FastAPI.
- Query PostgreSQL and generate concise executive commentary.

The first version is intentionally simple and runnable locally.

## Architecture

```text
Business Question
    |
API Boundary
    |
Identity / Policy Check
    |
Agent Runtime
    |
Tools / Retrieval / Data
    |
Evaluation / Guardrails
    |
Human Approval
    |
Decision Response
    |
Audit / Tracing / Metrics
```

The MVP starts with the API, semantic layer, PostgreSQL query path, and commentary response. Later stages add identity, policy, agent tools, guardrails, human approval, tracing, cost, latency, and quality monitoring.

## Tech Stack

- Backend: FastAPI, Python 3.11+, Pydantic, SQLAlchemy
- Database: PostgreSQL with Docker Compose
- AI Layer: OpenAI API via `OPENAI_API_KEY`, with mock commentary fallback
- Semantic Layer: YAML metric definitions
- Testing: pytest

## Learning Path

This project is also the working app for an AI Engineer learning path:

1. FastAPI: build a small API surface with validation and tests.
2. Docker + PostgreSQL: run the API against a real service dependency.
3. OpenAI Agents SDK: learn Agent, Tool, Handoff, and Guardrails.
4. Pydantic AI: add structured output and type-safe AI responses.
5. LangGraph: introduce State, Checkpoint, Interrupt, and Conditional Edges after the simpler runtime is understood.
6. Redis + Background Workers: support long-running tasks and task status checks.
7. Evaluation + Observability: measure answer quality, cost, latency, and failure modes.

The current implementation is Stage 1: `fastapi_mvp`.

The target is not a generic chatbot. The app should demonstrate how AI systems safely read enterprise data, use tools for analysis, validate responses, enforce role-based access, require human approval for high-risk actions, trace every agent execution, and monitor cost, latency, and quality.

## How to Run

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy environment variables:

```bash
cp .env.example .env
```

3. Start PostgreSQL. This requires Docker Desktop or Docker Engine:

```bash
docker compose up -d
```

4. Start FastAPI:

```bash
uvicorn app.main:app --reload
```

5. Test the API:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Why did operating profit miss budget in March?"}'
```

## API Endpoints

### `GET /health`

Checks API and database connectivity.

### `GET /metrics`

Returns metric definitions from `semantic_layer/metrics.yaml`.

### `POST /ask`

Example input:

```json
{
  "question": "Why did operating profit miss budget in March?"
}
```

Example response:

```json
{
  "answer": "Operating profit was below budget...",
  "sql_used": "SELECT ...",
  "metrics_used": ["operating_profit", "budget_variance"],
  "summary_type": "executive_commentary",
  "learning_stage": "fastapi_mvp"
}
```

## Example Questions

- Why did operating profit miss budget in March?
- Which business unit had the largest budget variance?
- How did revenue perform versus forecast?
- What drove margin pressure this month?
- Summarize March performance for the CFO.

## Future Enterprise Version with Databricks

A production enterprise version could add:

- Databricks Lakehouse for governed finance data.
- Unity Catalog for data governance and lineage.
- Databricks SQL or semantic models for certified metrics.
- LangGraph for multi-step planning and tool orchestration.
- Role-based access control, audit logs, and approval workflows.
- React dashboard for finance users.

Those components are intentionally excluded from this MVP to keep the first version easy to run, inspect, and present.

See `docs/learning_path.md` for the staged implementation plan.
