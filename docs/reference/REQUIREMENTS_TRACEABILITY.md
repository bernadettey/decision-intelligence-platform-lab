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

- Why did recognised revenue miss forecast in APAC this month?
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

- ARR.
- MRR.
- New ARR.
- Expansion ARR.
- Contraction ARR.
- Churned ARR.
- NRR.
- GRR.
- Billings.
- Deferred revenue.
- Recognised revenue.
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
| SaaS commercial and ARR | `master.customers`, `master.products`, `commercial.customer_contracts`, `commercial.subscriptions`, `commercial.subscription_events` |
| Customer billing and revenue recognition | `billing.customer_invoices`, `billing.customer_invoice_lines`, `billing.customer_payments`, `finance.revenue_schedules`, `finance.journal_headers`, `finance.journal_lines` |
| Professional Services | `services.projects`, `services.project_milestones`, `services.time_entries`, `billing.customer_invoices`, `finance.revenue_schedules`, `finance.journal_lines` |
| Supplier cost | `master.suppliers`, `procurement.purchases`, `procurement.purchase_lines`, `procurement.supplier_invoices`, `procurement.supplier_invoice_lines`, `finance.journal_lines` |
| People and OPEX | `master.employees`, `people.headcount_events`, `people.payroll`, `finance.journal_lines`, `finance.monthly_financials` |
| CAPEX and assets | `finance.capex_projects`, `finance.fixed_assets`, `finance.depreciation`, `finance.journal_headers`, `finance.journal_lines` |
| FX | `reference.fx_rates`, operational transaction tables, `finance.journal_headers`, `finance.journal_lines`, `finance.actuals`, `finance.monthly_financials` |
| Planning | `planning.budgets`, `planning.forecasts`, `planning.forecast_versions`, `planning.headcount_plan` |
| Security and audit | `security.users`, `security.roles`, `security.user_roles`, `security.data_access`, `security.audit_log` |
| Evaluation | `evaluation.scenarios`, `evaluation.scenario_ground_truth`, `evaluation.investigation_questions`, `evaluation.expected_answers`, `evaluation.agent_runs`, `evaluation.agent_feedback`, `evaluation.evaluation_results` |

Actual financial outcomes should ultimately be traceable from operational transactions through accounting/GL records into FP&A metrics. Requirements should therefore identify both operational evidence and finance/accounting tables where relevant.

Revenue requirements must distinguish operational SaaS metrics from recognised accounting revenue:

```text
Bookings != ARR / MRR != Billings != Recognised Revenue != Deferred Revenue != Cash
```

## Target Table Inventory

This inventory is documentation only, not SQL implementation.

| Area | Table | Status |
| --- | --- | --- |
| MASTER | `business_units` | CORE |
| MASTER | `regions` | CORE |
| MASTER | `departments` | CORE |
| MASTER | `cost_centres` | CORE |
| MASTER | `customers` | CORE |
| MASTER | `products` | CORE |
| MASTER | `suppliers` | CORE |
| MASTER | `employees` | CORE |
| MASTER | `gl_accounts` | CORE |
| MASTER | `currencies` | CORE |
| COMMERCIAL / SAAS | `leads` | SUPPORT |
| COMMERCIAL / SAAS | `opportunities` | SUPPORT |
| COMMERCIAL / SAAS | `customer_contracts` | CORE |
| COMMERCIAL / SAAS | `subscriptions` | CORE |
| COMMERCIAL / SAAS | `subscription_events` | CORE |
| PROFESSIONAL SERVICES | `projects` | CORE |
| PROFESSIONAL SERVICES | `project_milestones` | CORE |
| PROFESSIONAL SERVICES | `time_entries` | CORE |
| CUSTOMER BILLING | `customer_invoices` | CORE |
| CUSTOMER BILLING | `customer_invoice_lines` | CORE |
| CUSTOMER BILLING | `customer_payments` | SUPPORT |
| PROCUREMENT | `purchases` | CORE |
| PROCUREMENT | `purchase_lines` | CORE |
| PROCUREMENT | `supplier_invoices` | CORE |
| PROCUREMENT | `supplier_invoice_lines` | CORE |
| PEOPLE | `payroll` | CORE |
| PEOPLE | `headcount_events` | CORE-LITE / SUPPORT |
| FINANCE | `revenue_schedules` | CORE |
| FINANCE | `journal_headers` | CORE |
| FINANCE | `journal_lines` | CORE |
| FINANCE | `capex_projects` | SUPPORT |
| FINANCE | `fixed_assets` | SUPPORT |
| PLANNING | `budgets` | CORE |
| PLANNING | `forecasts` | CORE |
| PLANNING | `forecast_versions` | CORE |
| PLANNING | `headcount_plan` | CORE |
| REFERENCE / OPERATIONS | `business_events` | CORE |
| REFERENCE / OPERATIONS | `fx_rates` | CORE |
| EVALUATION | `scenarios` | CORE |
| EVALUATION | `scenario_ground_truth` | CORE |
| EVALUATION | `investigation_questions` | CORE |
| EVALUATION | `expected_answers` | CORE |
| EVALUATION | `agent_runs` | M2+ |
| EVALUATION | `agent_feedback` | M2+ |
| EVALUATION | `evaluation_results` | M7 |
| SECURITY | `users` | M6 |
| SECURITY | `roles` | M6 |
| SECURITY | `user_roles` | M6 |
| SECURITY | `data_access` | M6 |
| SECURITY | `audit_log` | M6 |
| FUTURE | `ai_usage` | FUTURE |
| FUTURE | AI economics / ROI / marginal resource allocation | FUTURE |

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

## Core Management Question Catalog

These questions are requirements inputs for future table and attribute design. They do not require implementation in this documentation task.

### Existing Core Questions

| ID | Management Question | Notes |
| --- | --- | --- |
| MQ-001 | Why did recognised revenue miss forecast? | Use recognised accounting revenue, not bookings or cash. |
| MQ-002 | Why did operating profit miss budget? | P&L variance investigation. |
| MQ-003 | Why did gross margin miss forecast? | May involve revenue mix, COGS, supplier cost, or FX. |
| MQ-004 | Which customer or product segment drove the revenue shortfall? | Distinguish SaaS ARR/billings from recognised revenue. |
| MQ-005 | Did supplier price increases explain the COGS variance? | Supplier-cost driver investigation. |
| MQ-006 | Did supplier volume or mix explain the COGS variance? | Procurement volume/mix investigation. |
| MQ-007 | Did FX movements materially affect margin? | Currency-sensitive revenue or supplier cost. |
| MQ-008 | Did cloud or infrastructure cost drive margin pressure? | Vendor/cloud cost investigation. |
| MQ-009 | Did contractor or vendor cost drive OPEX variance? | Procurement and people-adjacent OPEX. |
| MQ-010 | Did payroll variance drive OPEX variance? | People cost and payroll. |
| MQ-011 | Did headcount exceed plan? | Headcount vs planning. |
| MQ-012 | Did hiring delays create a vacancy benefit? | Lower OPEX may create future capacity risk. |
| MQ-013 | Did salary inflation affect EBITDA? | People-cost driver. |
| MQ-014 | Which business unit drove the forecast miss? | Conformed business-unit dimension. |
| MQ-015 | Which region drove the forecast miss? | Region dimension independent from BU/cost centre. |
| MQ-016 | Which cost centre drove OPEX variance? | Cost-centre dimension may be shared or nullable to BU. |
| MQ-017 | Did product mix deterioration affect margin? | Product and revenue/COGS mix. |
| MQ-018 | Did discounting affect revenue or margin? | Commercial pricing driver. |
| MQ-019 | Did customer churn affect ARR or recognised revenue? | Distinguish operational subscription metric from accounting revenue. |
| MQ-020 | Did a customer contract delay affect bookings, billings, or revenue? | Timing classification. |
| MQ-021 | Did CAPEX project timing affect cash flow or depreciation? | CAPEX/assets support, not full ERP. |
| MQ-022 | Did CAPEX overspend affect forecasted cash flow? | CAPEX investigation. |
| MQ-023 | How much revenue remains deferred? | Revenue recognition and balance-sheet timing. |
| MQ-024 | Did forecast assumptions explain the variance? | Planning assumption check. |
| MQ-025 | Which scenario best explains the observed KPI variance? | Evaluation/scenario linkage. |

### SaaS Core Extension

| ID | Management Question | Requirements Purpose |
| --- | --- | --- |
| MQ-S-001 | Why did recognised revenue miss forecast? | Ensures revenue schedules and GL linkage exist. |
| MQ-S-002 | Why did ARR grow while recognised revenue lagged? | Distinguishes subscription movement from accounting recognition. |
| MQ-S-003 | Why did billings exceed forecast but recognised revenue did not? | Distinguishes invoice/cash timing from revenue recognition. |
| MQ-S-004 | Which subscription events drove ARR movement? | Requires `NEW`, `RENEWAL`, `EXPANSION`, `CONTRACTION`, `CHURN`. |
| MQ-S-005 | Which customers drove churned ARR? | Requires customer/subscription event linkage. |
| MQ-S-006 | How much revenue remains deferred? | Requires billings, revenue schedules, and recognised revenue. |
| MQ-S-007 | Did revenue-recognition timing materially affect EBITDA? | Connects recognition timing to P&L impact. |

### Professional Services Core / Support Extension

| ID | Management Question | Requirements Purpose |
| --- | --- | --- |
| MQ-PS-001 | Why did Professional Services revenue miss forecast? | Keeps service revenue distinct from SaaS subscription revenue. |
| MQ-PS-002 | Was the miss driven by milestone timing, utilisation, or billable hours? | Requires project milestones and time entries. |
| MQ-PS-003 | Which projects drove margin deterioration? | Requires delivery cost and project revenue. |
| MQ-PS-004 | Are delivery costs above plan? | Requires project/cost planning and actuals. |
| MQ-PS-005 | Did project or milestone delays affect recognised revenue? | Connects delivery progress to revenue recognition. |

Do not build a full Professional Services Automation model. The purpose is only to support project revenue, utilisation, billable hours, delivery cost, project margin, and milestones.

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
