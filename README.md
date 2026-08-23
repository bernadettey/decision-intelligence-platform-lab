# Decision Intelligence Platform Lab

Decision Intelligence Platform Lab is a private learning and build lab for a future public Decision Intelligence Platform showcase. It is used to build governed, evidence-backed business decision workflows incrementally before selecting polished work for public presentation.

The first use case is **Business Performance / FP&A investigation**: answering questions such as why revenue, margin, or operating profit missed budget or forecast. FP&A is the first domain implementation, not the whole product identity.

## Project Constitution

This private lab repository exists to practice and develop the full path from AI Engineer to ML Engineer:

- Backend systems with clear API boundaries.
- Tool-using AI workflows grounded in structured business data.
- Data engineering pipelines that produce trusted analytical tables.
- Machine learning for forecasting, anomaly detection, and risk scoring.
- MLOps, deployment, evaluation, observability, and governance.

The project should grow incrementally. Do not create empty enterprise folders before they have real code, data, tests, or documentation to justify their existence.

## Current Stage

Current milestone: **M1 Enterprise Data Foundation & Backend**.

The existing implementation is a small FastAPI baseline with:

- Health, metrics, and ask endpoints.
- PostgreSQL-backed synthetic finance data.
- A YAML semantic layer for certified metrics.
- Deterministic mock commentary when no OpenAI key is configured.
- Focused tests for schema and semantic-layer behavior.

This baseline is preserved in Git as:

```text
prototype-fastapi-mvp-baseline-2026-08-22
```

## Milestone Roadmap

| Milestone | Theme | Purpose |
| --- | --- | --- |
| M1 | Enterprise Data Foundation & Backend | Establish the enterprise data architecture, scenario design, synthetic data foundation, PostgreSQL layer, and backend boundary required by later milestones. |
| M2 | Agentic Investigation | Add tool-using investigation workflows that can inspect approved evidence and produce traceable root-cause analysis. |
| M3 | Data Engineering | Build reliable raw-to-analytics pipelines and trusted analytical tables from generated operational and financial data. |
| M4 | Applied Machine Learning | Add forecasting, anomaly detection, or risk scoring using scenario-linked labels and outcomes. |
| M5 | MLOps | Track experiments, model versions, evaluation results, and reproducible inference behavior. |
| M6 | Cloud + Security + RLS | Add production-like deployment, identity, authorization, row-level security design, and audit controls. |
| M7 | Evaluation + Observability | Measure answer quality, tool choice, latency, cost, drift, security behavior, and failure modes. |

See [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md), [docs/M1_SCOPE.md](docs/M1_SCOPE.md), and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the working plan and finalized M1 architecture.

## Repository Shape

Only M1-relevant directories are kept in the active tree:

```text
app/                  FastAPI application code
database/             Local PostgreSQL schema and seed data
docs/                 Project plan, architecture notes, learning notes, experiments
semantic_layer/       Certified business metric definitions
tests/                Automated tests for the current implementation
```

Future areas such as agent orchestration, data pipelines, ML, MLOps, cloud infrastructure, security enforcement, and evaluation runners should be added when their milestone begins. The milestones are progressive layers of one platform, not separate demos.

## How To Run

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

3. Start PostgreSQL:

```bash
docker compose up -d
```

4. Start the API:

```bash
uvicorn app.main:app --reload
```

5. Try the current endpoints:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Why did operating profit miss budget in March?"}'
```

## Current API

- `GET /health`: checks API and database connectivity.
- `GET /metrics`: returns semantic metric definitions.
- `POST /ask`: answers a business performance question using the current M1 path.

## Engineering Rules

- Keep each milestone runnable and testable before moving to the next one.
- Commit every logical change with a clear message.
- Preserve old behavior before major restructures with a tag or snapshot.
- Prefer small, real modules over large empty architecture.
- FP&A examples should create reusable platform capability, not a narrow commentary generator.
