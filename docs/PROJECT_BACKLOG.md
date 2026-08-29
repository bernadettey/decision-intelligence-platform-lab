# Project Backlog

This backlog controls delivery priority and project execution order. It tracks deliverables, not learning topics.

The authoritative roadmap remains [PROJECT_PLAN.md](PROJECT_PLAN.md). This file translates that roadmap into the current working queue.

## Current

### M2.1a Agent Run Lifecycle

Status: Ready to scope next.

Goal: Implement deterministic agent-run lifecycle persistence and API boundaries without LLM or tools.

Expected next decision:

- Define the smallest coherent `agent` schema and `AgentState` persistence slice.
- Preserve existing M1 `/ask` behavior and regression tests.
- Do not add LLM calls, tools, configurable workflows, multi-agent runtime, M3 pipelines, ML, cloud, or RLS.

## Completed

- M1.1A Management Questions & Requirements Traceability.
- M1.1B Minimum Viable Enterprise Data Model.
- M1.1C Grain / Attributes / PK / FK / Relationships.
- M1.1D Scenario & Ground Truth Design.
- M1.2 PostgreSQL Schema V1 and V1.1 metadata foundation.
- M1.3 Phase 1 Synthetic Simulation Framework.
- M1.3 Phase 2 Deterministic Master Data Bootstrap.
- M1.3 Phase 3 SaaS Commercial Operational Flow.
- M1.4 PostgreSQL Data Layer.
- M1.5 Backend Foundation.
- Development governance: Maker-Reviewer workflow and compact Reviewer-to-Maker handoff.

## Next

- M2.1b First Controlled Capability.
- Early CI checkpoint.
- M2.2 Runtime Counters + Bounded Context.
- M2.3 Shape Validation + PolicyEvaluator.
- M2.4 Progressive Closure.
- M2.5 Failure + Timeout Handling.
- M2.6 HITL + Resume.
- M2.7 Observability Hardening.
- M2.8 Runtime Hardening + Tests.
- M2.9 Docker.
- M2.10 AWS Production Vertical Slice.

## Later

- Optional LangGraph comparison spike after the M2 baseline.
- M3 Data Engineering.
- M4 Applied Machine Learning.
- M5 MLOps.
- M6 Cloud + Security + RLS.
- M7 Evaluation + Observability.

## Scope Rules

- Project backlog determines delivery priority.
- Learning backlog informs teaching and implementation context but does not authorize scope expansion.
- Do not start later milestones unless the project backlog and task prompt explicitly authorize it.
