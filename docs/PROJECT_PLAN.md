# Project Plan

## North Star

Decision Intelligence Platform Lab is a private staged flagship project for learning and developing AI Engineer to ML Engineer capability.

The platform answers business decision questions by combining:

- Trusted metrics and data.
- API boundaries and typed schemas.
- Tool-using AI workflows.
- Forecasting, anomaly, or risk models.
- Evaluation, governance, observability, and deployment discipline.

The first implementation domain is Business Performance / FP&A investigation.

## Product Positioning

The lab is not an FP&A chatbot and not a commentary generator.

It is the private build space for a reusable decision workflow platform. FP&A is the first use case because budget, actual, forecast, variance, revenue, margin, and cost data make it easy to create clear ground truth for later agent and ML evaluation.

## Milestones

### M1: Backend Foundation

Goal: establish a clean, runnable backend foundation for business performance questions.

Scope:

- FastAPI application entrypoint.
- Health, metrics, and ask endpoints.
- PostgreSQL schema and seed data for synthetic business performance data.
- YAML semantic layer for certified metrics.
- Pydantic request and response schemas.
- Deterministic mock response path for local development.
- Focused tests.

Out of scope:

- Full agent orchestration.
- LangGraph.
- ML models.
- Cloud deployment.
- Production authentication.
- Frontend.

Acceptance:

- App imports successfully.
- Tests pass locally.
- API endpoints can be exercised against local services.
- README explains the current stage and the staged roadmap.

### M2: Agentic Application

Goal: turn the current ask endpoint into a traceable, tool-using analysis workflow.

Likely scope:

- Tool registry for metric lookup and variance queries.
- Simple agent runtime before complex graph orchestration.
- Structured reasoning outputs without exposing hidden chain of thought.
- Basic policy checks and response validation.
- Trace records for tool calls and evidence used.

### M3: Data Engineering

Goal: create reliable analytical data from raw or generated source data.

Likely scope:

- Synthetic raw data generation.
- Bronze, silver, and gold transformations.
- Data quality checks.
- Repeatable pipeline runs.
- Clear lineage from source data to certified business metrics.

### M4: Machine Learning

Goal: add predictive decision support.

Likely scope:

- Forecasting, anomaly detection, or risk scoring.
- Feature engineering.
- Train/evaluate split with known ground truth.
- Model inference interface used by the decision API.

### M5: MLOps

Goal: make model development reproducible and auditable.

Likely scope:

- Experiment tracking.
- Model versioning.
- Reproducible training runs.
- Evaluation reports.
- Promotion criteria for model use.

### M6: Cloud Deployment

Goal: deploy the platform with production-like operational discipline.

Likely scope:

- Container build.
- CI checks.
- Environment-specific configuration.
- Hosted API deployment.
- Secret handling and deployment documentation.

### M7: Evaluation & Observability

Goal: measure whether the decision workflow is correct, reliable, and worth trusting.

Likely scope:

- Benchmark question set with expected evidence and outputs.
- Agent/tool-use evaluation.
- Latency and cost tracking.
- Failure mode reporting.
- Quality dashboards or reports.

## Structure Rule

Only create what the current milestone needs.

M1 keeps active code under `app/`, `database/`, `semantic_layer/`, `tests/`, and `docs/`. Future milestone folders such as `pipelines/`, `ml/`, `infra/`, and `evaluation/` should be introduced when real milestone work begins.

## Next Issue Candidate

Issue #1 should start the actual M1 application cleanup after this constitution baseline:

**Issue #1: Clean M1 backend boundaries and remove fastapi_mvp identity from runtime response**

Expected work:

- Review current `app/` modules.
- Decide the smallest M1 package boundaries.
- Rename stage labels from demo-oriented `fastapi_mvp` to platform-oriented M1 language.
- Keep existing endpoints working.
- Update tests to lock the new M1 contract.
