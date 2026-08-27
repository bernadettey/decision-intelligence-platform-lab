# Project Backlog

This backlog controls delivery priority and project execution order. It tracks deliverables, not learning topics.

The authoritative roadmap remains [PROJECT_PLAN.md](PROJECT_PLAN.md). This file translates that roadmap into the current working queue.

## Current

### M1.4 PostgreSQL Data Layer

Status: Ready to scope next.

Goal: Build the local data access path for the backend.

Expected next decision:

- Define the smallest coherent PostgreSQL data-access slice before implementation.
- Preserve the existing schema and generated source-data architecture.
- Do not expand into M2 agents, M3 pipelines, ML, cloud, or RLS.

## Completed

- M1.1A Management Questions & Requirements Traceability.
- M1.1B Minimum Viable Enterprise Data Model.
- M1.1C Grain / Attributes / PK / FK / Relationships.
- M1.1D Scenario & Ground Truth Design.
- M1.2 PostgreSQL Schema V1 and V1.1 metadata foundation.
- M1.3 Phase 1 Synthetic Simulation Framework.
- M1.3 Phase 2 Deterministic Master Data Bootstrap.
- M1.3 Phase 3 SaaS Commercial Operational Flow.
- Development governance: Maker-Reviewer workflow and compact Reviewer-to-Maker handoff.

## Next

- M1.5 Backend Foundation.

## Later

- M2 Agentic Investigation.
- M3 Data Engineering.
- M4 Applied Machine Learning.
- M5 MLOps.
- M6 Cloud + Security + RLS.
- M7 Evaluation + Observability.

## Scope Rules

- Project backlog determines delivery priority.
- Learning backlog informs teaching and implementation context but does not authorize scope expansion.
- Do not start later milestones unless the project backlog and task prompt explicitly authorize it.
