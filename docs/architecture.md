# Decision Intelligence Platform Lab Architecture

## Overview

Decision Intelligence Platform Lab models a realistic B2B technology enterprise so business performance questions can be investigated from operational evidence through financial outcomes.

The current baseline simulates a monthly FP&A workflow for Budget vs Actual, Forecast vs Actual, Variance Analysis, Margin Analysis, and Executive Commentary. M1 refines this into an enterprise data foundation and backend boundary that later milestones can extend with agentic investigation, data engineering, applied ML, MLOps, cloud security, row-level security, evaluation, and observability.

The first version intentionally avoids Databricks, LangGraph, React, Kubernetes, and complex agent orchestration. It focuses on a small system that is easy to run and explain while preserving a path toward an enterprise-grade platform.

## Components

- FastAPI exposes `/health`, `/metrics`, and `/ask`.
- PostgreSQL stores synthetic FP&A actuals, budgets, forecasts, business units, and cost centres.
- SQLAlchemy manages database connectivity.
- The semantic layer defines metric names, formulas, synonyms, and allowed dimensions in YAML.
- The AI layer creates CFO-style commentary. If `OPENAI_API_KEY` is not set, it returns deterministic mock commentary for demo reliability.

## Target PostgreSQL Logical Schemas

M1 should define the logical database architecture before later milestones implement all behavior. The target PostgreSQL model uses schemas to separate enterprise concepts by responsibility.

### MASTER

Relatively stable enterprise entities and reference data.

- `business_units`
- `cost_centres`
- `regions`
- `products`
- `customers`
- `suppliers`
- `employees`
- `accounts`

`employees` should include `employee_id` and organizational relationships such as business unit, cost centre, region, manager, role, and employment status. This base model allows future employee- and role-based data access, row-level security, and audit behavior without redesigning the data foundation.

### OPERATIONS

Business activity and lower-grain operational events that explain what happened before the financial result.

- `orders`
- `order_lines`
- `invoices`
- `payments`
- `purchases`
- `supplier_invoices`
- `headcount_events`
- `business_events`
- `ai_usage`

`operations.ai_usage` is reserved for future AI economics fields such as:

- Application or workflow.
- Business unit.
- Employee or user.
- Model.
- Input and output tokens.
- Estimated model cost.
- Latency.

AI economics should not be implemented in M1. The future purpose of `operations.ai_usage` is to support questions such as:

- How much does AI cost?
- Where is AI spend allocated?
- Which AI workloads create economic value?
- What is the EBITDA impact?
- Is premium-model or token usage being allocated efficiently?

Future AI economics may include ROI, marginal benefit, marginal cost, and resource allocation. Those analyses are explicitly outside M1.

### FINANCE

Financial and accounting outcomes derived from operational activity, planning inputs, and accounting rules.

- `journal_entries`
- `actuals`
- `monthly_financials`
- `capex_projects`
- `fixed_assets`
- `depreciation`

The platform should eventually support P&L, CAPEX, and cash-flow investigation without attempting to implement a complete ERP or accounting system.

CAPEX and fixed-asset concepts are part of the architecture because some management questions depend on whether spend is expensed immediately or capitalized and recognized over time.

OPEX:

```text
OPEX -> expense -> EBITDA impact
```

CAPEX:

```text
CAPEX -> asset/cash outflow -> depreciation/amortisation later -> EBIT impact rather than direct initial EBITDA impact
```

### PLANNING

Budgets, forecasts, versions, and assumptions used to compare expected performance against actual outcomes.

- `budgets`
- `forecasts`
- `forecast_versions`
- `assumptions`

Planning data should preserve versions and assumptions so later investigations can explain whether a variance came from execution, timing, planning assumptions, or forecast quality.

### SECURITY

Future identity, authorization, row-level security, and audit support.

- `users`
- `roles`
- `user_roles`
- `data_access`
- `audit_log`

M1 should design for this layer, but full RLS enforcement is not part of M1 implementation. The future M6 implementation should use these concepts to test which users can access specific regions, business units, cost centres, customers, employees, and sensitive financial details.

### EVALUATION

Controlled scenarios and benchmark data used to evaluate agents, data pipelines, ML models, security behavior, and observability.

- `scenarios`
- `scenario_ground_truth`
- `investigation_questions`
- `expected_answers`

Evaluation data should remain separate from operational evidence. Agents may inspect approved business evidence, but evaluator-only truth data must remain hidden from the investigation runtime.

## Request Flow

1. User sends a question to `POST /ask`.
2. `SemanticService` infers relevant FP&A metrics from the question.
3. `QueryService` runs a variance query against PostgreSQL.
4. `AIService` generates executive commentary from the question, metrics, and query result.
5. API returns commentary, SQL used, metrics used, summary type, and the current learning stage.

## Target Enterprise AI Flow

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

This architecture is not a generic chatbot. It is intended to demonstrate the control points expected in an enterprise AI system:

- AI can read enterprise data only through approved tools and policy checks.
- Tools perform analysis against governed data sources instead of relying on model memory.
- Answers are validated before they become decision responses.
- User roles determine which data and actions are available.
- High-risk actions require human approval before completion.
- Every agent execution can be traced from question to tool calls to final response.
- Cost, latency, reliability, and answer quality can be monitored over time.

## Learning Architecture

The app should grow in this order:

1. FastAPI API surface.
2. Docker Compose and PostgreSQL service dependency.
3. OpenAI Agents SDK for basic agent runtime concepts, tool use, handoff, and guardrails.
4. Pydantic AI for structured, type-safe AI outputs and response validation.
5. LangGraph for durable runtime concerns such as state, checkpointing, interrupts, conditional edges, and human approval.
6. Redis and background workers for long-running jobs.
7. Evaluation and observability for tracing, cost, latency, and production AI quality control.

The reason for this sequence is to learn what an agent runtime does before adopting a graph runtime. LangGraph should enter only when the app has a real need for state, resumability, branching, or human interruption.

## Enterprise Direction

A later enterprise version could move governed financial data and semantic models into Databricks, add orchestration with LangGraph, add permissions and audit trails, and expose a richer frontend.
