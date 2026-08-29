# Project Plan

## North Star

Decision Intelligence Platform Lab is a private staged learning project for building one Decision Intelligence Platform from M1 through M7.

The platform answers business decision questions by combining trusted enterprise data, clear API boundaries, tool-using AI workflows, forecasting or risk models, governance, evaluation, observability, and deployment discipline.

The first implementation domain is Business Performance / FP&A investigation. FP&A is the first use case, not the whole product identity.

## Documentation Map

- High-level architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- M1 boundary: [M1_SCOPE.md](M1_SCOPE.md)
- Project execution backlog: [PROJECT_BACKLOG.md](PROJECT_BACKLOG.md)
- Learning backlog: [LEARNING_BACKLOG.md](LEARNING_BACKLOG.md)
- Logical data model: [reference/DATA_MODEL.md](reference/DATA_MODEL.md)
- Requirements traceability: [reference/REQUIREMENTS_TRACEABILITY.md](reference/REQUIREMENTS_TRACEABILITY.md)
- Scenario and evaluation model: [reference/SCENARIO_MODEL.md](reference/SCENARIO_MODEL.md)
- Security and answerability: [reference/SECURITY_AND_ANSWERABILITY.md](reference/SECURITY_AND_ANSWERABILITY.md)
- Future AI economics: [reference/AI_ECONOMICS_FUTURE.md](reference/AI_ECONOMICS_FUTURE.md)

Read reference documents only when they are relevant to the current issue.

Project backlog determines delivery priority. Learning backlog informs teaching and implementation context but does not authorize scope expansion.

## Roadmap

| Milestone | Theme | Platform Capability |
| --- | --- | --- |
| M1 | Enterprise Data Foundation + Backend | Management-question requirements, enterprise data model, revenue recognition design, scenario design, SQL schema, synthetic data, PostgreSQL layer, and backend boundary. |
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
| M1.1A | Management Questions & Requirements Traceability | Canonical management-question requirements, including SaaS revenue recognition and Professional Services questions. |
| M1.1B | Minimum Viable Enterprise Data Model | Smallest B2B SaaS + Professional Services model that supports FP&A investigation without blocking later milestones. |
| M1.1C | Grain / Attributes / PK / FK / Relationships | Clear table grain, fields, primary keys, foreign keys, and organizational relationships. |
| M1.1D | Scenario & Ground Truth Design | Evaluator-only ground truth and agent-visible evidence model. |
| M1.2 | SQL Schema | PostgreSQL schema aligned to the M1 model, including simplified core revenue-recognition structures. |
| M1.3 | Synthetic Data Generator | Driver-based synthetic data generation. |
| M1.4 | PostgreSQL Data Layer | Local data access path for the backend. |
| M1.5 | Backend Foundation | FastAPI boundary and tests for current M1 capability. |

## M2 Implementation Sequence

M2 is **Agentic Investigation**. M2 adds a separate agent-run API while
preserving the existing M1 `/ask` flow.

| Step | Name | Output |
| --- | --- | --- |
| M2.1a | Agent Run Lifecycle | `agent` schema, `agent_runs`, `AgentState`, repository, runtime lifecycle, `MAX_STEPS`, idempotent `POST /agent/runs`, `GET /agent/runs/{run_id}`, optimistic versioning, status and closure reason. No LLM and no tool. |
| M2.1b | First Controlled Capability | M2 `LLMClient`, normalized usage, first read-only tool, `agent_steps`, and first controlled loop through existing M1 service/repository boundaries. |
| Early CI checkpoint | Regression gate | GitHub Actions running pytest on push/PR while preserving M1 behavior. |
| M2.2 | Runtime Counters + Bounded Context | Runtime counters and deterministic bounded context assembly. |
| M2.3 | Shape Validation + PolicyEvaluator | Proposed-action validation and side-effect-free deterministic policy decisions. |
| M2.4 | Progressive Closure | Step, LLM, tool, token, cost, duplicate-action, and evidence-sufficiency closure controls. |
| M2.5 | Failure + Timeout Handling | Failure-aware retries, timeout behavior, and terminal-state persistence. |
| M2.6 | HITL + Resume | Persisted pause/resume support without bypassing runtime policy. |
| M2.7 | Observability Hardening | `agent_llm_calls`, per-call telemetry, minimal pricing, and queryable usage. |
| M2.8 | Runtime Hardening + Tests | Production-oriented regression and failure-mode coverage. |
| M2.9 | Docker | Containerized runtime support for the M2 application. |
| M2.10 | AWS Production Vertical Slice | CI/CD, ECR, ECS/Fargate, PostgreSQL, IAM/secrets, health/logging/basic monitoring, and rollback awareness. |

Optional after the M2 baseline:

- LangGraph comparison spike.

## M2 Architecture Freeze

M2 builds one controlled production-style agentic application that is stateful,
durable, testable, observable, cost-aware, bounded, failure-aware,
HITL-capable, and deployable.

Principle:

```text
LLM proposes.
Deterministic runtime code validates, authorizes, executes, persists,
stops/retries, and escalates.
```

M2 has exactly one hardcoded workflow. `workflow="saas_arr_v1"` is descriptive
version metadata only, not a workflow registry key.

Do not introduce `WorkflowDefinition`, `WorkflowRegistry`, `WorkflowFactory`, or
configurable workflow abstractions until a second materially different agent
task appears with different tools, prompts/goals, budgets, or stages.

## M1 Out Of Scope

M1 should design for, but not implement:

- Agent orchestration or LangGraph.
- Databricks or Spark pipelines.
- ML models or MLflow.
- Cloud deployment.
- Full RLS/security enforcement.
- AI ROI optimization.
- Marginal resource allocation optimization.

## M2 Out Of Scope

M2 does not implement:

- Write-capable tools.
- LLM-generated SQL execution.
- Multi-agent runtime.
- Multiple configurable workflows.
- Workflow definition, registry, or factory abstractions.
- RAG, embeddings, fine-tuning, or advanced memory/context summarization.
- Semantic duplicate detection.
- Mandatory LangGraph or LangChain without concrete need.
- Kubernetes/EKS, multi-region, Kafka, or sharding.
- Full LLMOps platform, advanced dashboards/alerts, or dynamic model routing.
- Async queue architecture unless a real requirement appears.

## Structure Rule

Keep active implementation small and milestone-bound. Do not create empty future architecture folders. Add code, data, tests, or infrastructure only when a current issue needs them.

Current implementation areas remain:

- `app/`
- `database/`
- `semantic_layer/`
- `tests/`
- `docs/`
