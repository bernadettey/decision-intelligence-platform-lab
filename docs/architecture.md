# Decision Intelligence Platform Architecture

## Overview

This MVP simulates a monthly FP&A workflow for Budget vs Actual, Forecast vs Actual, Variance Analysis, Margin Analysis, and Executive Commentary.

The first version intentionally avoids Databricks, LangGraph, React, Kubernetes, and complex agent orchestration. It focuses on a small system that is easy to run and explain on GitHub.

## Components

- FastAPI exposes `/health`, `/metrics`, and `/ask`.
- PostgreSQL stores synthetic FP&A actuals, budgets, forecasts, business units, and cost centres.
- SQLAlchemy manages database connectivity.
- The semantic layer defines metric names, formulas, synonyms, and allowed dimensions in YAML.
- The AI layer creates CFO-style commentary. If `OPENAI_API_KEY` is not set, it returns deterministic mock commentary for demo reliability.

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
