# AI Engineer Learning Path

This project is the practical learning app. Each stage should leave the app runnable, testable, and explainable.

The target system is not a chatbot. It is an enterprise AI workflow:

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

The learning goal is to show how AI safely reads enterprise data, uses tools to complete analysis, validates answers, respects role-based access, pauses high-risk actions for approval, traces each execution, and monitors cost, latency, and quality.

## Stage 1: FastAPI

Goal: expose a small, reliable API for an AI workflow.

Build:

- `GET /health` checks service and database connectivity.
- `GET /metrics` reads metric definitions from `semantic_layer/metrics.yaml`.
- `POST /ask` accepts a finance question and returns executive commentary.
- Pydantic request and response models define the API contract.

Acceptance checks:

- `pytest` passes.
- `/health` returns `status: ok` when PostgreSQL is available.
- `/metrics` returns YAML-backed metric definitions.
- `/ask` returns `learning_stage: fastapi_mvp`.

## Stage 2: Docker + PostgreSQL

Goal: run the API against a real service dependency.

Build:

- PostgreSQL runs through Docker Compose.
- Seed data supports deterministic demo questions.
- App configuration comes from `.env`.
- Database failures are visible through `/health`.

Acceptance checks:

- `docker compose up -d` starts PostgreSQL.
- FastAPI can query seeded finance data.
- The app can be restarted without manual database setup.

## Stage 3: OpenAI Agents SDK

Goal: understand what a simple agent runtime provides.

Build:

- One finance analyst agent.
- One or two tools, such as metric lookup and variance query.
- A small handoff example only if there is a clear second role.
- Guardrails for unsupported questions, unsafe SQL behavior, or policy violations.

Acceptance checks:

- The agent can call the metric and query tools.
- Unsupported requests return a controlled response.
- The non-agent `/ask` behavior remains available for comparison.

## Stage 4: Pydantic AI

Goal: make AI output structured and type-safe.

Build:

- Typed commentary output with fields such as `summary`, `drivers`, `risks`, and `recommended_actions`.
- Validation for missing or malformed model output.
- Tests for deterministic mock structured output.

Acceptance checks:

- API returns structured JSON, not only prose.
- Invalid AI output is caught before reaching the user.
- Tests cover the response schema.

## Stage 5: LangGraph

Goal: learn why production runtimes need durable state.

Build:

- A graph state object for question, metrics, SQL, rows, draft answer, and review status.
- Conditional edges for supported versus unsupported questions.
- Checkpointing for resumable workflows.
- Interrupt for human review or high-risk approval before final commentary.

Acceptance checks:

- A workflow can resume from a checkpoint.
- A human review interrupt can pause and continue.
- State transitions are visible in tests or logs.

## Stage 6: Redis + Background Workers

Goal: support long-running AI jobs.

Build:

- Submit async analysis jobs.
- Store job status and results.
- Add a worker process for background execution.
- Use Redis for queue or transient state.

Acceptance checks:

- API returns a job id immediately.
- A status endpoint shows queued, running, succeeded, or failed.
- Failed jobs keep enough error detail for debugging.

## Stage 7: Evaluation + Observability

Goal: operate the AI system like a production service.

Build:

- Fixed evaluation questions.
- Expected output criteria for financial reasoning and citation/metric use.
- Logs for latency, model, token usage, tool calls, and errors.
- Basic regression checks before changing prompts or runtimes.
- Execution traces connect the business question, policy checks, tool calls, guardrail results, approval status, and final response.

Acceptance checks:

- Evaluation can run locally.
- Changes to prompts or tools can be compared against previous results.
- The app exposes enough telemetry to debug quality and reliability.
