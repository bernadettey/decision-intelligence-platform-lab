# Loops

This project uses loop engineering as an implementation discipline.

A loop is a repeatable workflow that can be triggered, verified, measured, and improved. Loops should start as documented checks before becoming automation.

## Loop Contract

Each loop should define:

- Trigger: what starts the loop.
- Goal: what the loop is trying to achieve.
- Inputs: source data, code, question set, policies, or configuration.
- Actions: steps the loop performs.
- Verifier: how correctness is checked.
- Outputs: files, logs, results, API responses, or metrics produced.
- Stop Condition: when the loop is considered complete.
- Metrics: numbers used to track quality, speed, cost, or reliability.

## Priority v1 Loops

1. Build Loop: keep the app importable and runnable.
2. Test Loop: keep automated tests passing.
3. API Validation Loop: verify `/health`, `/metrics`, and `/ask`.
4. Semantic Layer Validation Loop: verify metric definitions and inference.
5. Benchmark Evaluation Loop: measure answer quality over fixed questions.
6. Tool Calling Loop: verify expected tools are used when agent workflows are added.
7. Audit Logging Loop: make each decision traceable.
8. Latency and Cost Tracking Loop: measure runtime performance and model cost.

## Implementation Rule

Do not build a full loop engine first. Implement loops manually until repeated patterns are clear. Add YAML loop definitions and a Python runner only after two or three loops have real execution paths and stored results.
