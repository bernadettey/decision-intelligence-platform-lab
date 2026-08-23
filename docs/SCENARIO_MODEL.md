# Scenario Model

## Purpose

The scenario model defines how synthetic business conditions become controlled evidence for investigation, benchmark truth for evaluation, and feedback for platform improvement.

This document defines the scenario, evaluation, and feedback model only. It does not implement the synthetic data generator, evaluation framework, runtime agent behavior, SQL, tests, or application code.

## Causal Investigation Chain

Synthetic data generation should follow this chain:

```text
Business Event
    -> Operational Driver
    -> Transaction / Operational Data
    -> Accounting / GL Flow
    -> Financial Outcome
    -> KPI Variance
    -> Management Question
```

Financial outcomes should be derived from underlying drivers wherever practical. They should not be unrelated random numbers.

Example:

```text
Supplier price increase
    -> unit cost increases
    -> purchase and supplier invoice costs increase
    -> GL postings increase COGS
    -> gross margin decreases
    -> operating profit misses forecast
    -> management asks why margin missed forecast
```

## Scenario Types

Base scenario types should include:

- `supplier_price_increase`
- `customer_contract_delay`
- `customer_churn`
- `sales_volume_decline`
- `discounting_campaign`
- `product_mix_deterioration`
- `hiring_delay`
- `headcount_overspend`
- `contractor_cost_increase`
- `FX_shock`
- `cloud_cost_spike`
- `unexpected_marketing_spend`
- `capex_project_delay`
- `capex_project_overspend`
- `capex_timing_shift`

These scenarios cover customer, supplier, people/OPEX, CAPEX/assets, FX, and financial-accounting investigation paths.

## Agent-Visible Evidence vs Evaluator-Only Truth

The architecture separates evidence from answer keys.

### `operations.business_events`

Business evidence that the investigation agent may be allowed to discover.

Examples:

- Supplier price notice.
- Customer contract delay.
- Customer churn event.
- Sales volume change.
- Discounting campaign.
- Hiring plan change.
- Contractor cost increase.
- FX rate shock.
- Cloud cost spike.
- Marketing spend approval.
- CAPEX project delay or overspend.

Agent access to this evidence should eventually depend on user identity, employee/role relationships, business unit, cost centre, region, customer, supplier, and policy.

### `evaluation.scenario_ground_truth`

Evaluator-only benchmark data containing the injected cause and expected causal chain.

The investigation agent must never access `evaluation.scenario_ground_truth`.

Ground truth should support:

- Scenario ID.
- Injected business event.
- Affected entity or dimension.
- Expected driver.
- Expected financial impact.
- Expected KPI impact.
- Primary root cause.
- Expected causal chain.
- Severity.
- Expected investigation questions.

## Permanent Evaluation Schema

The evaluation schema is permanent and should include:

- `scenarios`
- `scenario_ground_truth`
- `investigation_questions`
- `expected_answers`
- `agent_runs`
- `agent_feedback`
- `evaluation_results`

### `evaluation.scenarios`

Scenario registry and metadata.

Future fields may include:

- Scenario ID.
- Scenario type.
- Period.
- Severity.
- Affected business unit.
- Affected region.
- Affected product, customer, supplier, employee, or project.
- Active/inactive status.

### `evaluation.scenario_ground_truth`

Evaluator-only injected truth and causal chain.

This table is the answer key. It must not be exposed through investigation tools, retrieval, prompts, or agent-visible APIs.

### `evaluation.investigation_questions`

Management questions generated from scenarios.

Examples:

- Why did gross margin miss forecast in APAC?
- Why did operating profit miss budget?
- Was the revenue shortfall driven by churn, contract delay, or volume?
- Did FX or supplier price movements explain COGS variance?
- Did CAPEX timing affect cash flow or depreciation?

### `evaluation.expected_answers`

Expected answer requirements for each investigation question.

Expected answers should describe:

- Required root cause.
- Required KPI impact.
- Required evidence.
- Required dimensions.
- Acceptable wording variants.
- Claims that would be unsupported or incorrect.

### `evaluation.agent_runs`

Observed investigation attempts.

Future records should capture:

- Agent run ID.
- Scenario ID.
- Question ID.
- User or role context.
- Access scope.
- Tools used.
- Evidence retrieved.
- Final answer.
- Runtime status.
- Latency and cost metadata where appropriate.

AI token economics remain a later-milestone concern. M1 may reserve the relationship but should not implement ROI, marginal cost, marginal benefit, or allocation optimization.

### `evaluation.agent_feedback`

Human or evaluator feedback on an agent run.

Feedback should record:

- Correct root cause.
- Incorrect or missing causal link.
- Correct evidence use.
- Missed evidence.
- Unsupported claim.
- Security or RLS issue.
- Reviewer comment.
- Suggested correction.

### `evaluation.evaluation_results`

Structured evaluation output.

Future results may include:

- Scenario ID.
- Agent run ID.
- Score.
- Pass/fail status.
- Root-cause accuracy.
- Evidence accuracy.
- KPI accuracy.
- Security compliance.
- Latency/cost observations.
- Regression comparison against previous runs or versions.

## Roadmap Evolution

Ground truth starts in M1 and evolves across the roadmap:

- M1: scenario definition and evaluator-only ground truth model.
- M2: agent investigation benchmark using approved evidence only.
- M3: data pipeline validation from generated operational activity to analytical tables.
- M4: ML labels and outcome validation.
- M5: model-version comparison.
- M6: security/RLS expected behavior.
- M7: automated evaluation and observability.

## Example Scenario Trace

```text
Scenario:
  supplier_price_increase

Business event:
  Supplier raises unit price for APAC infrastructure purchases.

Operational driver:
  Unit cost increases while purchase quantity remains stable.

Operational data:
  purchases and supplier_invoices show higher unit prices.

Accounting / GL flow:
  journal_entries post higher COGS.

Financial outcome:
  actual COGS exceeds forecast.

KPI variance:
  gross margin and operating profit miss forecast.

Management question:
  Why did APAC gross margin miss forecast?

Expected investigation path:
  identify APAC margin miss
  -> inspect COGS variance
  -> inspect supplier invoices and purchase prices
  -> connect supplier price increase to GL/actuals
  -> explain margin and operating profit impact

Ground truth:
  primary root cause is supplier_price_increase.
```

## Access Rule

`evaluation.scenario_ground_truth` is evaluator-only and must never be accessible to the investigation agent. This is a platform requirement, not only an implementation detail.
