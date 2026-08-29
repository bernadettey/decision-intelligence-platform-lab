# Codex Instructions

Follow the shared working rules in:

`/Users/bernadette/ai-coworker-rules.md`

## Repository Identity

This repository is **Decision Intelligence Platform Lab**: a private learning lab for building one progressive Decision Intelligence Platform from M1 through M7.

The first use case is Business Performance / FP&A investigation, but the platform should remain reusable and not become a single-purpose FP&A commentary tool.

## Before Starting Work

1. Read `docs/PROJECT_PLAN.md`.
2. Identify the current milestone and issue.
3. Read only documentation relevant to the current task.
4. Do not load unrelated reference documents unless required.
5. Run `git status --short --branch` before modifying files.
6. Inspect `git diff` before committing.
7. Keep commits logically scoped.
8. Do not silently expand architecture or project scope.

## Documentation Routing

General repository work:
- `docs/PROJECT_PLAN.md`

Delivery priority:
- `docs/PROJECT_BACKLOG.md`

Learning context:
- `docs/LEARNING_BACKLOG.md`

Architecture changes:
- `docs/ARCHITECTURE.md`

Data model / management requirements:
- `docs/reference/DATA_MODEL.md`
- `docs/reference/REQUIREMENTS_TRACEABILITY.md`

Synthetic scenarios / ground truth / evaluation:
- `docs/reference/SCENARIO_MODEL.md`

Agent safety / ambiguity / answerability / authorization:
- `docs/reference/SECURITY_AND_ANSWERABILITY.md`

AI economics / token economics / resource allocation:
- `docs/reference/AI_ECONOMICS_FUTURE.md`

## Current Boundary

Current milestone: **M2 Agentic Investigation**.

M1 is complete. Preserve the existing `/ask` flow:

`FastAPI -> SemanticService -> QueryService -> PostgresReadRepository -> business PostgreSQL -> AIService`

M2 introduces a separate agent-run API. Do not route `/ask` through `AgentRuntime`.

Before M2 implementation:

1. Read `docs/PROJECT_PLAN.md`.
2. Read `docs/ARCHITECTURE.md`.
3. Read the current milestone/backlog item.
4. Inspect relevant code.
5. Do not implement future milestones.

Preserve FastAPI -> Service -> Repository boundaries. Prefer deterministic runtime controls over prompt-only constraints. Make one bounded change at a time.

Do not start future milestone implementation until the current milestone scope is explicit. Do not create empty future architecture folders. Add directories only when they contain real code, tests, data, or documentation to justify their existence.

## Development Roles

The task prompt determines the current role.

MAKER:
- Implements the assigned task.
- Follows authoritative repository documentation.
- Keeps scope narrow.
- Runs relevant validation.
- Reviews diff before commit.
- Reports implementation decisions.
- After each M2 implementation slice, lists files changed, explains request/data flow, runs relevant tests, inspects git diff, and stops for human review.

REVIEWER:
- Performs independent review.
- Defaults to read-only on first review.
- Does not silently rewrite the Maker's implementation.
- Checks correctness, architecture, tests, production failure modes, security/data integrity where relevant, and scope compliance.
- Classifies findings as `BLOCKER`, `MAJOR`, `MINOR`, or `SUGGESTION`.
- Outputs must end with a compact `MAKER HANDOFF`.

MAKER handoff rule:
- Validate handoff findings against the actual code before implementing fixes.

Backlog rule:
- Project backlog determines delivery priority.
- Learning backlog informs teaching and implementation context but does not authorize scope expansion.
