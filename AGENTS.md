# Codex Instructions

Follow the shared working rules in:

`/Users/bernadette/ai-coworker-rules.md`

## Project Identity

This repository is **Decision Intelligence Platform**.

The first use case is Business Performance / FP&A investigation, but the repository should remain a reusable decision-intelligence platform rather than becoming a single-purpose FP&A commentary tool.

## Working Rules

- Confirm the repository root with `git rev-parse --show-toplevel` before meaningful edits.
- Check `git status --short --branch` before and after changes.
- Preserve the current implementation before major restructure work with a tag or snapshot.
- Keep commits small and logical.
- Do not start future milestone implementation until the current milestone scope is explicit.
- Do not create empty future architecture folders. Add directories only when they contain real code, tests, data, or documentation.
- Before recommending a push, inspect staged files and avoid committing secrets or local environment files.

## Current Boundary

Current milestone: **M1 Backend Foundation**.

Do not start Issue #1 application implementation as part of the restructuring baseline. This step is only for project constitution, roadmap, documentation, and M1 structure cleanup.
