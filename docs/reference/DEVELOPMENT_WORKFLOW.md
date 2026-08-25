# Development Workflow

This document defines a lightweight human-supervised Maker-Reviewer workflow for using Codex and Claude Code on this repository.

This is a development governance workflow only. It is not the application's runtime agent architecture.

## Workflow

```text
Specification
-> Maker implementation
-> Commit + automated tests
-> Independent Reviewer full review
-> Compact MAKER HANDOFF
-> Maker validates and fixes findings
-> Fix commit + automated tests
-> Reviewer delta re-review
-> Human approval
```

For simple work where no independent review is requested, the shorter flow is:

```text
Specification
-> Maker implementation
-> Independent Reviewer
-> Review findings
-> Maker fixes
-> Reviewer re-check
-> Automated validation
-> Human approval
-> Accept / merge
```

## Roles

### Maker

The Maker owns implementation.

Responsibilities:

- Implement the assigned task.
- Follow the authoritative repository documentation.
- Keep scope narrow.
- Explain important implementation decisions.
- Add or run appropriate validation.
- Review the diff before completion or commit.
- Respond to review findings.

### Reviewer

The Reviewer is an independent checker.

Responsibilities:

- Default to read-only on the first review pass.
- Review the actual diff and the relevant specification.
- Check correctness, architecture, tests, production failure modes, security/data integrity where relevant, and scope compliance.
- Look for edge cases and failure modes, not only style.
- Avoid approving based only on code appearance.
- Do not silently rewrite the Maker's implementation.

Findings should be classified as:

- `BLOCKER`: must fix before acceptance.
- `MAJOR`: likely correctness, safety, integrity, or maintainability issue.
- `MINOR`: small issue with limited risk.
- `SUGGESTION`: optional improvement.

## Reviewer-to-Maker Handoff

The Reviewer may perform a detailed internal or full review, but must end with a compact self-contained `MAKER HANDOFF` for the implementing agent.

The handoff should contain only actionable findings needed for the next implementation step. It must be understandable without the full review text.

Use this structure for each included finding:

```text
Severity:
Disposition:
Location:
Problem:
Required outcome:
Validation:
```

Severity values:

- `BLOCKER`
- `MAJOR`
- `MINOR`
- `SUGGESTION`

Disposition values:

- `FIX NOW`
- `DEFER`

Handoff rules:

- `BLOCKER` + `FIX NOW` must always be included.
- `MAJOR` + `FIX NOW` must always be included.
- `MINOR` should be included only when it should realistically be fixed now.
- `SUGGESTION` should normally be omitted unless required by another finding.
- Resolved checks, praise, and general observations should not be repeated.
- Keep `MAKER HANDOFF` under approximately 500 words where practical.

## Maker Handoff Response

The Maker must not blindly implement Reviewer findings.

For each `FIX NOW` finding, the Maker should:

- Validate the finding against the actual code.
- State whether the Maker agrees.
- Fix confirmed `BLOCKER` and `MAJOR` findings.
- Address included `MINOR` findings when low risk and appropriate.
- Explain disagreements instead of silently ignoring them.
- Run relevant automated validation.

## Delta Re-review

After the Maker produces a fix commit, the Reviewer should normally review:

- The original `MAKER HANDOFF`.
- The fix commit diff.
- Affected tests.

The Reviewer should not perform a full deep review of unchanged architecture unless:

- The fix changes foundational transaction, security, or schema behavior.
- A regression is suspected.
- The Human Approver requests it.

For each previous finding, return one of:

- `RESOLVED`
- `PARTIALLY RESOLVED`
- `NOT RESOLVED`

Then provide the final verdict.

### Human Approver

The Human Approver controls final acceptance.

Responsibilities:

- Decide whether findings are acceptable.
- Control final acceptance or merge.
- Reject either agent's conclusion when needed.
- Resolve tradeoffs between scope, risk, timing, and learning goals.

### Automated Validation

Tests and validation are independent gates.

Agreement between two AI agents is not proof of correctness. Passing tests are also not complete proof, but they provide a separate evidence source and should be used whenever relevant.

## Role Rotation

Codex and Claude Code are not permanently assigned to one role.

Initial convention for the next module:

- M1.3 Simulation Framework: Codex = `MAKER`
- M1.3 Simulation Framework: Claude Code = `REVIEWER`

Roles may rotate at clean module boundaries.

Guidelines:

- Keep one Maker through a tightly coupled implementation unit.
- Rotate roles when moving to a sufficiently independent module or domain.
- Use the non-authoring agent for independent review when practical.
- Do not create a complicated automatic rotation system.

## Runtime Boundary

This Maker-Reviewer workflow is for development governance.

It is not evidence that the Decision Intelligence runtime should use a multi-agent architecture. Runtime architecture remains single-agent-first unless later evidence justifies extra complexity.

Multi-agent runtime should only be introduced if supported by evidence such as:

- Excessive tool or context complexity.
- Clearly separable specialist responsibilities.
- Different security or policy boundaries.
- Evaluation results showing specialist routing is beneficial.

Avoid premature multi-agent orchestration.

## Worktree And Concurrency

- Do not allow two Maker agents to edit the same working tree concurrently.
- Maker-Reviewer does not require parallel editing.
- Reviewer can inspect a completed Maker diff or commit before fixes are made.
- If parallel implementation experiments are ever required, use separate Git branches or worktrees.
- Do not create branches or worktrees solely to perform ordinary review.

## Context Discipline

Keep short instruction files concise:

- `AGENTS.md`
- `CLAUDE.md`

Detailed workflow rationale belongs here. Do not duplicate large architecture sections into instruction files.

Do not pass full Reviewer reasoning to the Maker when a compact actionable handoff is sufficient. Permanent architecture knowledge belongs in authoritative repository docs. Temporary review reasoning remains temporary.

Do not create one-off review Markdown files for every review. Only update permanent docs when a review produces a durable architectural or engineering decision.
