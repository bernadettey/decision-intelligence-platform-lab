# Codex Implementation Plan

## Product Direction

This project is an AI Engineer learning app for the private Decision Intelligence Platform Lab.

It is not a chatbot. The target workflow is:

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

The first version should stay small, runnable, and testable. It should create a clean foundation for later agent, governance, evaluation, and observability work.

## Architecture Decision

The platform starts as a modular monolith. It is deployed as a single application, while internal modules are separated by domain boundaries such as API, governance, agent runtime, tools, evaluation, and observability.

As scale, ownership, or deployment requirements evolve, selected modules can be extracted into independent services.

## Implementation Rule

Do not build a large empty enterprise skeleton.

Each module should be added only when it has at least one real responsibility, test, route, policy, dataset, or execution path.

## Version 1 Scope

Version 1 focuses on:

- FastAPI API boundary.
- PostgreSQL-backed finance data.
- YAML semantic layer.
- Deterministic mock commentary fallback.
- Basic response schema validation.
- First engineering loops for build, test, API validation, and semantic validation.

Version 1 does not include:

- Full OpenAI Agents SDK implementation.
- LangGraph runtime.
- Redis background workers.
- Full Loop Engine.
- Production authentication.
- Full RAG document retrieval.
- Complex frontend.

## Target v1 Structure

The original `backend/` package has been renamed to `app/`. It can be migrated gradually toward:

```text
app/
    main.py
    api/
        dependencies.py
        routes/
            health.py
            metrics.py
            analytics.py
    core/
        config.py
        exceptions.py
        security.py
    schemas/
        analytics.py
        governance.py
        observability.py
    services/
        semantic_service.py
        query_service.py
        commentary_service.py
    tools/
        metric_lookup.py
        variance_query.py
        registry.py
    governance/
        rbac.py
        policy_engine.py
        audit.py
    observability/
        tracing.py
        metrics.py
        cost_tracking.py
    infrastructure/
        database.py
        llm_client.py
```

Migration should be incremental. Keep tests passing after each step.

## Loop Contract

Every important workflow should be written as a loop before it becomes automation.

Each loop should define:

- Trigger: what starts the loop.
- Goal: what the loop is trying to achieve.
- Inputs: source data, code, question set, policies, or configuration.
- Actions: steps the loop performs.
- Verifier: how correctness is checked.
- Outputs: files, logs, results, API responses, or metrics produced.
- Stop Condition: when the loop is considered complete.
- Metrics: numbers used to track quality, speed, cost, or reliability.

## Priority Loops for v1

### 1. Build Loop

Goal: keep the app importable and runnable.

Actions:

- Import the FastAPI app.
- Check configuration loading.
- Start the app locally when needed.

Verifier:

- App imports without exception.

Stop Condition:

- Import and startup checks pass.

Metrics:

- Startup success.
- Startup time.

### 2. Test Loop

Goal: keep automated tests passing.

Actions:

- Run `pytest`.
- Fix failing tests or code.
- Run `pytest` again.

Verifier:

- Pytest exit code is `0`.

Stop Condition:

- All tests pass.

Metrics:

- Test pass rate.
- Failed test count.
- Test runtime.

### 3. API Validation Loop

Goal: verify the public API boundary.

Actions:

- Call `GET /health`.
- Call `GET /metrics`.
- Call `POST /ask`.
- Validate status codes and response schemas.

Verifier:

- Responses match expected schemas.
- `/ask` returns `learning_stage: fastapi_mvp`.

Stop Condition:

- All endpoint checks pass.

Metrics:

- Status code success rate.
- API latency.
- Schema validation failures.

### 4. Semantic Layer Validation Loop

Goal: keep finance metric definitions reliable.

Actions:

- Load `semantic_layer/metrics.yaml`.
- Validate required fields.
- Test metric inference against benchmark questions.

Verifier:

- Each metric has `description`, `formula`, `synonyms`, and `allowed_dimensions`.
- Known questions map to expected metrics.

Stop Condition:

- All semantic checks pass.

Metrics:

- Metric coverage.
- Inference match rate.
- YAML validation errors.

### 5. Benchmark Evaluation Loop

Goal: measure AI answer quality over a fixed question set.

Actions:

- Run benchmark business questions.
- Capture answers.
- Compare against expected metric usage and commentary criteria.
- Save results.

Verifier:

- Required metrics and answer fields are present.
- Commentary meets minimum quality rules.

Stop Condition:

- Evaluation score meets the v1 threshold.

Metrics:

- Accuracy.
- Required metric usage.
- JSON validity.
- Commentary quality score.

### 6. Tool Calling Loop

Goal: verify that agent or tool-based workflows use the right tools.

Actions:

- Define expected tools for each benchmark question.
- Run the analysis workflow.
- Compare expected tools with actual tools.

Verifier:

- Expected tools are called.
- Unnecessary tools are not called.

Stop Condition:

- Tool precision and recall meet threshold.

Metrics:

- Tool precision.
- Tool recall.
- Tool error rate.

### 7. Audit Logging Loop

Goal: make each decision traceable.

Actions:

- Record the business question.
- Record user or role context when available.
- Record policy decision.
- Record tool calls.
- Record final response.
- Record timestamp and latency.

Verifier:

- Required audit fields are present for each execution.

Stop Condition:

- Audit records are complete for all tested executions.

Metrics:

- Audit completeness.
- Missing field count.

### 8. Latency and Cost Tracking Loop

Goal: understand runtime performance and AI cost.

Actions:

- Measure API latency.
- Measure tool latency.
- Track model and token usage when real LLM calls are enabled.
- Estimate cost per request.

Verifier:

- Metrics are emitted for each execution.

Stop Condition:

- Latency and cost data are available for tested executions.

Metrics:

- End-to-end latency.
- Tool latency.
- Prompt tokens.
- Completion tokens.
- Estimated cost.

## First Codex Build Sequence

### Step 1: Stabilize Current MVP

- Keep current `/health`, `/metrics`, and `/ask` behavior.
- Keep `.venv/bin/pytest` passing.
- Add tests for response schemas and semantic metric loading.
- Avoid adding new frameworks.

### Step 2: Introduce Modular Monolith Shape

- Keep `app/main.py` as the FastAPI entrypoint.
- Split routes into `app/api/routes/`.
- Move config and database into `app/core/` and `app/infrastructure/`.
- Keep compatibility simple and update imports carefully.

### Step 3: Add Tool Boundary

- Convert metric lookup and variance query into explicit tool-like modules.
- Keep them callable without an agent runtime.
- Add tests for tool input and output.

### Step 4: Add Basic Governance

- Add simple role context.
- Add policy checks for allowed metrics or allowed actions.
- Add audit records for each analysis request.

### Step 5: Add First Evaluation Dataset

- Add `evals/datasets/finance_questions.jsonl`.
- Add expected metrics and answer criteria.
- Add a script or pytest test to run the benchmark loop.

### Step 6: Add Basic Observability

- Add request timing.
- Add tool timing.
- Add structured execution trace objects.
- Track token and cost only when real LLM calls are enabled.

## Later Iterations

### Agent Runtime

- Add OpenAI Agents SDK after tool boundaries exist.
- Use existing tools instead of rewriting business logic.
- Add guardrails for unsupported questions and unsafe tool use.

### Pydantic AI

- Add structured commentary outputs.
- Validate AI-generated fields before returning them.
- Keep deterministic mock output for tests.

### LangGraph

- Add only when the workflow needs durable state, checkpointing, conditional edges, or human approval interrupts.
- Start with one workflow, such as executive commentary review.

### Redis and Background Workers

- Add when analysis jobs become long-running.
- Add job submission, status, result, and failure handling.

### Full Loop Engine

- Add YAML loop definitions and a Python loop runner only after at least two or three loops are implemented manually and their shared shape is clear.

## Non-Goals for Early Versions

- Do not build microservices.
- Do not add Databricks, Kubernetes, or React in the first implementation pass.
- Do not create empty folders for every future enterprise concept.
- Do not store or expose hidden model reasoning. Trace observable execution evidence instead.
- Do not optimize for a polished UI before the API, evaluation, governance, and observability story is credible.
