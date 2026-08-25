# Claude Code Instructions

This repository is **Decision Intelligence Platform Lab**.

Use the same authoritative project documents as Codex:

- General roadmap: `docs/PROJECT_PLAN.md`
- High-level architecture: `docs/ARCHITECTURE.md`
- Data model decisions: `docs/reference/DATA_MODEL.md`
- Development workflow: `docs/reference/DEVELOPMENT_WORKFLOW.md`

## Working Rules

- Read only the task-relevant authoritative docs.
- Treat `docs/reference/DATA_MODEL.md` as authoritative for data-model decisions.
- Respect frozen architecture unless explicitly asked to redesign it.
- Check `git status --short --branch` before changing files.
- Inspect `git diff` before completion.
- Obey the MAKER or REVIEWER role specified by the task.
- REVIEWER defaults to read-only unless explicitly asked to implement fixes.
- REVIEWER mode must end with a compact `MAKER HANDOFF` suitable for direct use by the Maker.
- Re-review should normally be delta-focused.
- Do not confuse development Maker-Reviewer workflow with the application's future runtime agent architecture.
