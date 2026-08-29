# Learning Backlog

This backlog tracks engineering knowledge gaps discovered during implementation. It does not control delivery scope and does not authorize implementation or architecture expansion.

Use this file when learning context is relevant to the task. For the broader curriculum, see [learning_path.md](learning_path.md).

## Now

### Concept

Pytest fixtures and fake repositories.

Trigger/context:

M1.3 tests use fake repositories for unit tests and real PostgreSQL for integration tests.

Learning goal:

Understand when to isolate business logic with fakes and when to use integration tests for database constraints, transactions, and rollback behavior.

### Concept

Simulation transaction boundaries.

Trigger/context:

M1.3 Phase 1 required STARTED batch persistence, business transaction rollback, FAILED metadata persistence, and atomic success clock advancement.

Learning goal:

Explain why batch lifecycle metadata and generated business writes need different transaction handling.

## Next

### Concept

Deterministic agent runtime controls.

Trigger/context:

M2 architecture freezes the principle that the LLM proposes while deterministic runtime code validates, authorizes, executes, persists, stops/retries, and escalates.

Learning goal:

Understand why production agent systems need deterministic policy, lifecycle, budget, and persistence controls around LLM calls.

### Concept

SQL grain / join cardinality / join fan-out.

Trigger/context:

M1.4 exposed a 1:N subscription-to-events join that could multiply ARR/MRR during aggregation.

Learning goal:

Understand table grain, 1:1 / 1:N / N:N relationships, aggregation grain, and how to prevent metric duplication.

### Concept

Duplicate protection vs idempotency.

Trigger/context:

Repeated deterministic SaaS bootstrap currently rejects existing deterministic IDs.

Learning goal:

Understand reject-on-duplicate vs idempotent retry/upsert behavior and when each is appropriate.

### Concept

PostgreSQL constraints as safety rails.

Trigger/context:

M1.2 and M1.3 rely on PK/FK/CHECK constraints for schema integrity and bootstrap validation.

Learning goal:

Read constraint failures and connect them back to data model design decisions.

### Concept

Deterministic synthetic data.

Trigger/context:

M1.3 uses `random_seed`, `generator_version`, and deterministic IDs for reproducible bootstrap data.

Learning goal:

Understand reproducibility, replay, and idempotency at a practical generator level.

## Later

### Concept

Dead / unreachable code.

Trigger/context:

Reviewer noted the region_id fallback is unreachable because customer.region_id is NOT NULL.

Learning goal:

Recognise unreachable branches and understand when cleanup is worth doing.

### Concept

Revenue recognition flow.

Trigger/context:

Upcoming transaction generation must distinguish bookings, billings, recognised revenue, deferred revenue, and cash.

Learning goal:

Understand the simplified M1 revenue-recognition model before building revenue-generating records.

### Concept

Operational-to-GL lineage.

Trigger/context:

Future phases need transactions to connect to journal headers and journal lines without creating duplicate financial truth.

Learning goal:

Trace operational evidence through accounting actuals into FP&A metrics.

## Parking Lot

### Concept

Stale MVP ORM model cleanup.

Trigger/context:

`app/models.py` still contains early MVP ORM models that are not aligned to the V1 schema.

Learning goal:

Recognise dead or stale compatibility code and decide when cleanup should be deferred versus included in a scoped change.

### Concept

CDC, MERGE, and watermark ingestion.

Trigger/context:

V1.1 schema includes metadata for future ingestion patterns, but M1.3 should not implement M3 pipelines.

Learning goal:

Learn these after the source generator is stable.

### Concept

Runtime agent architecture.

Trigger/context:

The development workflow uses Maker-Reviewer roles, but runtime remains single-agent-first.

Learning goal:

Separate development governance from application runtime design.

## Completed

### Concept

Repository and remote basics.

Trigger/context:

Earlier setup clarified local repo path, branch, GitHub remote, and push flow.

Learning goal:

Distinguish local working tree, Git branch, remote repository, commit, and push.

### Concept

VS Code PostgreSQL inspection.

Trigger/context:

Earlier setup used `ms-ossdata.vscode-pgsql` to inspect local PostgreSQL.

Learning goal:

Connect to the local database and distinguish schema/seed files from live database state.
