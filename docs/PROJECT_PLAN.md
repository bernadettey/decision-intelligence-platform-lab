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

These milestones build one Decision Intelligence Platform progressively. They are not separate demos. Each milestone should extend the same enterprise model, evidence trail, and decision workflow foundation.

| Milestone | Theme | Platform Capability |
| --- | --- | --- |
| M1 | Enterprise Data Foundation & Backend | Enterprise data model, scenario design, synthetic data foundation, PostgreSQL layer, and backend boundary. |
| M2 | Agentic Investigation | Tool-using root-cause investigation over approved evidence. |
| M3 | Data Engineering | Repeatable pipelines from operational events to analytical data products. |
| M4 | Applied Machine Learning | Forecasting, anomaly detection, and risk scoring over scenario-linked outcomes. |
| M5 | MLOps | Experiment tracking, model versioning, reproducible training, and promotion criteria. |
| M6 | Cloud + Security + RLS | Cloud-ready deployment, identity, authorization, row-level security, and audit behavior. |
| M7 | Evaluation + Observability | Automated evaluation, traces, telemetry, cost, reliability, and failure-mode monitoring. |

### M1: Enterprise Data Foundation & Backend

Goal: establish the enterprise data architecture required by later milestones and keep a clean, runnable backend boundary for business performance questions.

M1 should model a realistic B2B technology enterprise with enough structure to support future FP&A investigation, agentic root-cause analysis, data engineering, ML, MLOps, security/governance, and evaluation. M1 is not only an API cleanup milestone; it is the data foundation for the rest of the platform.

M1 workstreams:

#### M1.1 Enterprise Data Model

Define the logical enterprise entities and relationships that later milestones will use for business performance investigation. This includes master data, operational activity, finance outcomes, planning data, security/audit concepts, and evaluation scenarios.

The target PostgreSQL architecture should use logical schemas for `master`, `operations`, `finance`, `planning`, `security`, and `evaluation`. See [architecture.md](architecture.md) for the schema responsibilities and target table set.

#### M1.2 Scenario & Ground Truth Design

Define controlled business scenarios and evaluator-only ground truth so future agents, pipelines, and models can be tested against known causes and expected impacts.

Synthetic data should follow a causal investigation chain from business event to operational driver, transaction data, financial outcome, KPI variance, and management question. The investigation runtime may eventually inspect approved records in `operations.business_events`, but it must never access evaluator-only `evaluation.scenario_ground_truth`.

#### M1.3 Synthetic Data Generator

Design the generator approach for realistic operational and financial data. The implementation should eventually derive financial outcomes from underlying business drivers wherever practical instead of producing unrelated random numbers.

#### M1.4 PostgreSQL Data Layer

Design and implement the local PostgreSQL data layer needed for M1, with clear logical schemas and enough data to support business performance questions.

#### M1.5 Backend Foundation

Keep the FastAPI application boundary clean and runnable. The backend should expose current M1 capabilities while leaving clear extension points for later agent, data, ML, security, and evaluation layers.

M1 implementation should explicitly exclude:

- Agent orchestration.
- LangGraph.
- Databricks or Spark pipelines.
- ML models.
- MLflow.
- Cloud deployment.
- Full row-level security enforcement.
- AI ROI optimization.
- Marginal resource allocation optimization.

M1 should still design the data structures needed to support those later capabilities.

Acceptance:

- M1 documentation defines the target enterprise data model, scenario design, and milestone boundary.
- App imports successfully.
- Tests pass locally.
- API endpoints can be exercised against local services.
- README explains that M1 establishes the data architecture and backend boundary for one progressive platform.

### M2: Agentic Investigation

Goal: turn the current ask endpoint into a traceable, tool-using investigation workflow.

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

### M6: Cloud + Security + RLS

Goal: deploy the platform with production-like operational and security discipline.

Likely scope:

- Container build.
- CI checks.
- Environment-specific configuration.
- Hosted API deployment.
- Secret handling and deployment documentation.
- Identity and role model implementation.
- Row-level security policy implementation and tests.
- Audit logging for sensitive data access.

### M7: Evaluation + Observability

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
