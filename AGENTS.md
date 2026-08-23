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

Architecture changes:
- `docs/ARCHITECTURE.md`

Data model / management requirements:
- `docs/reference/REQUIREMENTS_TRACEABILITY.md`

Synthetic scenarios / ground truth / evaluation:
- `docs/reference/SCENARIO_MODEL.md`

Agent safety / ambiguity / answerability / authorization:
- `docs/reference/SECURITY_AND_ANSWERABILITY.md`

AI economics / token economics / resource allocation:
- `docs/reference/AI_ECONOMICS_FUTURE.md`

## Current Boundary

Current milestone: **M1 Enterprise Data Foundation + Backend**.

Do not start future milestone implementation until the current milestone scope is explicit. Do not create empty future architecture folders. Add directories only when they contain real code, tests, data, or documentation to justify their existence.
