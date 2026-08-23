# Requirements Traceability

## Purpose

Requirements traceability connects management questions to the data, scenarios, expected investigation path, agent result, and feedback loop used to judge the platform.

The traceability chain is:

```text
Management Question
    -> Intent / Metric / Entity Resolution
    -> Required Capability
    -> KPI / Metric
    -> Comparison Basis
    -> Dimensions
    -> Drivers
    -> Required Tables
    -> Required Attributes
    -> Authorization Requirement
    -> Data Sufficiency
    -> Expected Answerability
    -> Missing Data Behaviour
    -> Expected Investigation Path
    -> Scenario
    -> Ground Truth
    -> Agent Result
    -> Feedback
```

This document defines the requirement model. It does not implement application code, SQL, tests, generators, or runtime behavior.

## Traceability Fields

The requirements model should support:

- `question_id`
- `persona`
- `business_question`
- `decision_type`
- `primary_metric`
- `comparison_basis`
- `dimensions`
- `drivers`
- `required_capabilities`
- `required_tables`
- `required_attributes`
- `authorization_requirement`
- `expected_answerability`
- `ambiguity_behavior`
- `missing_data_behavior`
- `scenario_type`
- `expected_investigation_path`
- `ground_truth_type`
- `priority_milestone`

### Management Question

The user-facing business question.

Examples:

- Why did gross margin miss forecast in APAC this month?
- Why did operating profit miss budget for Enterprise Software?
- Which customer or product segment drove the revenue shortfall?
- Did supplier price increases or FX movements explain the COGS variance?
- Did delayed hiring improve EBITDA but create future delivery risk?
- Did a CAPEX project timing shift affect cash flow, depreciation, or EBIT?

### Intent / Metric / Entity Resolution

The interpretation step that determines what the user is asking, which metric is implied, and which entity or dimension scope applies.

Examples:

- "How are we doing?" may resolve to a multi-metric summary.
- "Why are we doing badly in APAC?" requires explicit KPI interpretation or clarification.
- "Why did margin miss forecast?" resolves to gross margin or operating margin depending on context.

### Required Capability

The platform capability needed to answer the question.

Examples:

- Metric calculation.
- Variance analysis.
- Driver investigation.
- Scenario benchmark evaluation.
- Authorization-aware data access.
- Evidence sufficiency assessment.
- Abstention or clarification.

### KPI / Metric

The metric or outcome being investigated.

Examples:

- Revenue.
- Gross margin.
- COGS.
- OPEX.
- EBITDA.
- EBIT.
- Operating profit.
- Cash flow.
- CAPEX spend.
- Depreciation.
- Forecast accuracy.

### Comparison Basis

The baseline used to judge performance.

Examples:

- Actual vs budget.
- Actual vs forecast.
- Current period vs prior period.
- Current forecast vs prior forecast version.
- Scenario actual vs expected answer.

### Dimensions

The entity grain used to slice the investigation.

Required base dimensions include:

- Business unit.
- Cost centre.
- Region.
- Product.
- Customer.
- Supplier.
- Employee.
- Manager.
- Account.
- Forecast version.
- Scenario.
- Currency.
- Period.

Employee and organizational dimensions must support future RLS/governance by connecting `employee_id` to business unit, cost centre, region, manager, role, and access scope.

### Drivers

The business mechanism that caused the KPI movement.

Examples:

- Customer contract delay.
- Customer churn.
- Sales volume decline.
- Discounting campaign.
- Product mix deterioration.
- Supplier price increase.
- Contractor cost increase.
- Headcount overspend.
- Hiring delay.
- Cloud cost spike.
- Unexpected marketing spend.
- FX shock.
- CAPEX project delay.
- CAPEX project overspend.
- CAPEX timing shift.

### Attributes

The specific fields required to explain the driver.

Examples:

- Customer ID, segment, contract value, renewal date, churn status.
- Product ID, unit price, discount rate, unit volume, product margin.
- Supplier ID, purchase price, quantity, invoice date, payment terms.
- Employee ID, role, manager, business unit, cost centre, region, start/end date.
- Account ID, account type, GL posting date, debit, credit, currency.
- CAPEX project ID, budget, actual spend, asset ID, in-service date, useful life.
- FX rate, transaction currency, functional currency, rate date, realized/unrealized impact.

### Tables

The source tables needed to answer or evaluate the question.

Representative mapping:

| Requirement Area | Tables |
| --- | --- |
| Enterprise hierarchy | `master.business_units`, `master.cost_centres`, `master.regions`, `master.employees` |
| Customer revenue | `master.customers`, `master.products`, `operations.orders`, `operations.order_lines`, `operations.invoices`, `operations.payments` |
| Supplier cost | `master.suppliers`, `operations.purchases`, `operations.supplier_invoices`, `finance.journal_entries`, `finance.actuals` |
| People and OPEX | `master.employees`, `operations.headcount_events`, `finance.journal_entries`, `finance.monthly_financials` |
| CAPEX and assets | `finance.capex_projects`, `finance.fixed_assets`, `finance.depreciation`, `finance.journal_entries` |
| FX | operational transaction tables, `finance.journal_entries`, `finance.actuals`, `finance.monthly_financials` |
| Planning | `planning.budgets`, `planning.forecasts`, `planning.forecast_versions`, `planning.assumptions` |
| Security and audit | `security.users`, `security.roles`, `security.user_roles`, `security.data_access`, `security.audit_log` |
| Evaluation | `evaluation.scenarios`, `evaluation.scenario_ground_truth`, `evaluation.investigation_questions`, `evaluation.expected_answers`, `evaluation.agent_runs`, `evaluation.agent_feedback`, `evaluation.evaluation_results` |

Actual financial outcomes should ultimately be traceable from operational transactions through accounting/GL records into FP&A metrics. Requirements should therefore identify both operational evidence and finance/accounting tables where relevant.

### Authorization Requirement

The required access scope before evidence can be exposed.

Examples:

- Persona can access APAC margin.
- Persona cannot access EMEA payroll.
- Persona can access aggregated business-unit results but not employee-level detail.

Authorization is separate from answerability. A question can be answerable by the platform and still denied for a specific user.

### Data Sufficiency

Whether the required data exists for the requested analysis.

Examples:

- Required tables and attributes exist.
- Revenue and churn exist, but NPS does not.
- Operational evidence exists, but causal evidence is incomplete.

### Expected Answerability

Use exactly:

- `SUPPORTED`
- `PARTIALLY_SUPPORTED`
- `UNSUPPORTED`

### Ambiguity Behavior

Use exactly:

- `AUTO_RESOLVE`
- `ASK_CLARIFICATION`
- `MULTI_METRIC_SUMMARY`

Ambiguous questions are not automatically unsupported.

### Missing Data Behaviour

Define what the agent should do when evidence is missing.

Examples:

- Answer the supported part and state the limitation.
- Ask for clarification.
- Abstain from unsupported causal claims.
- Deny access without exposing protected data.

### Scenario

The controlled scenario that injects or represents the business condition.

Examples:

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

### Expected Investigation Path

The expected evidence sequence an agent should follow.

Example:

```text
Gross margin missed forecast
    -> identify affected region and product line
    -> compare actual COGS against forecast COGS
    -> inspect supplier invoice prices and purchase quantities
    -> inspect FX-sensitive purchases
    -> connect supplier price or FX movement to GL/actuals
    -> explain margin variance against forecast
```

### Ground Truth

The evaluator-only answer key.

Ground truth should include:

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

`evaluation.scenario_ground_truth` must never be accessible to the investigation agent.

### Agent Result

The observed output from an agent run.

Future records should connect to:

- Question.
- User/context.
- Allowed access scope.
- Tools used.
- Evidence retrieved.
- Metrics calculated.
- Answer produced.
- Confidence or quality indicators.
- Runtime, cost, and failure metadata where appropriate.

### Feedback

Feedback records whether the agent result met the expected investigation path and answer requirements.

Feedback should support:

- Correct root cause.
- Correct KPI impact.
- Correct evidence selection.
- Missed evidence.
- Unsupported claim.
- Security or access violation.
- Overbroad answer.
- Human reviewer comments.
- Evaluation score.

## FX Requirement

FX must be represented in the base requirements because B2B technology companies often transact across currencies. Requirements should preserve:

- Transaction currency.
- Functional currency.
- Rate date.
- Applied exchange rate.
- FX-sensitive revenue, supplier cost, cash, or accounting postings.
- Whether variance is operational, pricing, volume, mix, timing, or FX-driven.

## AI Usage Boundary

AI usage and token economics are reserved for later milestones. Traceability may reserve future links to `operations.ai_usage`, `evaluation.agent_runs`, and `evaluation.evaluation_results`, but M1 should not implement AI ROI, marginal benefit, marginal cost, or allocation optimization.

## Intentional Negative Requirements

Some requirements should remain unsupported to test abstention and evidence boundaries. Do not add datasets merely to make these answerable.

Negative/boundary examples:

- NPS decline.
- Customer satisfaction causing revenue decline.
- Employee engagement causing productivity decline.
- Competitor pricing causing churn.

Correct behavior is to investigate supported adjacent evidence only when useful, state the missing evidence clearly, and avoid unsupported causal claims.
