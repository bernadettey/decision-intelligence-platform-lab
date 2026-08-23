# M1 Scope

## M1 Definition

M1 is **Enterprise Data Foundation + Backend**.

M1 establishes the data architecture required by later milestones while preserving a clean, runnable backend boundary. It is not a standalone demo and not a one-off FP&A commentary tool.

## M1 Workstreams

### M1.1 Enterprise Data Model

Define a realistic B2B technology enterprise model across:

- `master`
- `operations`
- `finance`
- `planning`
- `security`
- `evaluation`

The model must include customers, suppliers, people/OPEX, CAPEX/assets, FX, and accounting/GL flows. Financial outcomes should ultimately be traceable from operational transactions through GL/accounting into FP&A metrics.

### M1.2 Scenario & Ground Truth Design

Define controlled business scenarios and evaluator-only ground truth. The scenario model should support known causes, expected investigation paths, expected answers, agent feedback, and evaluation results.

`evaluation.scenario_ground_truth` must never be available to the investigation agent.

See [reference/SCENARIO_MODEL.md](reference/SCENARIO_MODEL.md) for detailed scenario and evaluation requirements.

### M1.3 Synthetic Data Generator

Design synthetic data generation around business drivers and causal chains. Financial values should ultimately be derived from underlying operational activity wherever practical, not generated as unrelated random numbers.

M1 may define generator requirements and structure. This documentation task does not implement a generator.

### M1.4 PostgreSQL Data Layer

Define the target PostgreSQL logical schemas and table responsibilities. The data layer should support future data engineering, ML, MLOps, security/RLS, and evaluation without requiring an architectural rewrite.

### M1.5 Backend Foundation

Maintain a clean FastAPI backend boundary for current M1 capabilities. The backend should remain runnable and testable while leaving clear extension points for later agent, data, ML, security, and evaluation layers.

## Explicitly Out Of M1 Implementation

M1 must not implement:

- Agent orchestration.
- LangGraph.
- Databricks or Spark pipelines.
- ML models.
- MLflow.
- Cloud deployment.
- Full RLS enforcement.
- AI ROI optimization.
- Marginal resource allocation optimization.

M1 should still design the data structures needed to support these later.

## AI Usage Boundary

AI usage and token economics are reserved for later milestones. The base architecture may reserve `operations.ai_usage`, but M1 should not attempt to calculate AI ROI, marginal benefit, marginal cost, or optimal model/token allocation.

Future fields may include:

- Application or workflow.
- Business unit.
- Employee or user.
- Model.
- Input and output tokens.
- Estimated model cost.
- Latency.

## Acceptance Criteria

M1 documentation should make these things clear:

- The platform is one progressive system from M1 through M7.
- M1 is the enterprise data foundation plus backend boundary.
- The logical schemas are `master`, `operations`, `finance`, `planning`, `security`, and `evaluation`.
- Employee identity and organizational relationships support future RLS/governance.
- Financial outcomes can eventually be traced from operational transactions through GL/accounting into FP&A metrics.
- Evaluation ground truth is separate from agent-visible evidence.
- AI usage economics is a later-milestone concern, not M1 implementation.

Detailed requirements traceability lives in [reference/REQUIREMENTS_TRACEABILITY.md](reference/REQUIREMENTS_TRACEABILITY.md). Detailed security and answerability policy lives in [reference/SECURITY_AND_ANSWERABILITY.md](reference/SECURITY_AND_ANSWERABILITY.md). Future AI economics boundaries live in [reference/AI_ECONOMICS_FUTURE.md](reference/AI_ECONOMICS_FUTURE.md).
