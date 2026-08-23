# Project Plan

## North Star

Decision Intelligence Platform Lab is a private staged learning project for building one Decision Intelligence Platform from M1 through M7.

The platform answers business decision questions by combining trusted enterprise data, clear API boundaries, tool-using AI workflows, forecasting or risk models, governance, evaluation, observability, and deployment discipline.

The first implementation domain is Business Performance / FP&A investigation. FP&A is the first use case, not the whole product identity.

## Documentation Map

- High-level architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- M1 boundary: [M1_SCOPE.md](M1_SCOPE.md)
- Requirements traceability: [reference/REQUIREMENTS_TRACEABILITY.md](reference/REQUIREMENTS_TRACEABILITY.md)
- Scenario and evaluation model: [reference/SCENARIO_MODEL.md](reference/SCENARIO_MODEL.md)
- Security and answerability: [reference/SECURITY_AND_ANSWERABILITY.md](reference/SECURITY_AND_ANSWERABILITY.md)
- Future AI economics: [reference/AI_ECONOMICS_FUTURE.md](reference/AI_ECONOMICS_FUTURE.md)

Read reference documents only when they are relevant to the current issue.

## Roadmap

| Milestone | Theme | Platform Capability |
| --- | --- | --- |
| M1 | Enterprise Data Foundation + Backend | Management-question requirements, enterprise data model, scenario design, SQL schema, synthetic data, PostgreSQL layer, and backend boundary. |
| M2 | Agentic Investigation | Tool-using root-cause investigation over approved evidence. |
| M3 | Data Engineering | Repeatable pipelines from operational events to analytical data products. |
| M4 | Applied Machine Learning | Forecasting, anomaly detection, and risk scoring over scenario-linked outcomes. |
| M5 | MLOps | Experiment tracking, model versioning, reproducible training, and promotion criteria. |
| M6 | Cloud + Security + RLS | Cloud-ready deployment, identity, authorization, row-level security, and audit behavior. |
| M7 | Evaluation + Observability | Automated evaluation, traces, telemetry, cost, reliability, and failure-mode monitoring. |

Future capabilities after the core roadmap:

- AI Economics.
- Causal Inference.
- Optimisation / Resource Allocation.

These future capabilities must not expand M1 implementation scope.

## Current M1 Sequence

M1 is **Enterprise Data Foundation + Backend**.

| Step | Name | Output |
| --- | --- | --- |
| M1.1A | Management Questions & Requirements Traceability | Canonical management-question requirements and answerability expectations. |
| M1.1B | Minimum Viable Enterprise Data Model | Smallest enterprise model that supports FP&A investigation without blocking later milestones. |
| M1.1C | Grain / Attributes / PK / FK / Relationships | Clear table grain, fields, primary keys, foreign keys, and organizational relationships. |
| M1.1D | Scenario & Ground Truth Design | Evaluator-only ground truth and agent-visible evidence model. |
| M1.2 | SQL Schema | PostgreSQL schema aligned to the M1 model. |
| M1.3 | Synthetic Data Generator | Driver-based synthetic data generation. |
| M1.4 | PostgreSQL Data Layer | Local data access path for the backend. |
| M1.5 | Backend Foundation | FastAPI boundary and tests for current M1 capability. |

## M1 Out Of Scope

M1 should design for, but not implement:

- Agent orchestration or LangGraph.
- Databricks or Spark pipelines.
- ML models or MLflow.
- Cloud deployment.
- Full RLS/security enforcement.
- AI ROI optimization.
- Marginal resource allocation optimization.

## Structure Rule

Keep active implementation small and milestone-bound. Do not create empty future architecture folders. Add code, data, tests, or infrastructure only when a current issue needs them.

Current implementation areas remain:

- `app/`
- `database/`
- `semantic_layer/`
- `tests/`
- `docs/`
