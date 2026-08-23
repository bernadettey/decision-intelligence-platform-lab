# Architecture

## Purpose

Decision Intelligence Platform Lab is a private learning lab for building one progressive Decision Intelligence Platform from M1 through M7. The first domain is Business Performance / FP&A investigation, but the architecture is not a single-purpose FP&A demo.

M1 is **Enterprise Data Foundation + Backend**. It establishes the enterprise data model, scenario design, synthetic data foundation, PostgreSQL layer, and backend boundary required by later milestones.

Later milestones should extend this same platform:

- M2: Agentic Investigation.
- M3: Data Engineering.
- M4: Applied Machine Learning.
- M5: MLOps.
- M6: Cloud + Security + RLS.
- M7: Evaluation + Observability.

## Core Architecture Decision

The platform models a realistic B2B technology enterprise. It must support future investigation across:

- Customer and revenue flows.
- Supplier and purchasing flows.
- People, headcount, contractor, and OPEX flows.
- CAPEX, fixed assets, depreciation, and asset timing.
- FX exposure and exchange-rate impacts.
- Accounting and GL flows.
- FP&A planning, actuals, forecasts, and variance analysis.
- Security, governance, audit, and future row-level security.
- Evaluation scenarios, ground truth, feedback, and benchmark results.

Actual financial outcomes should ultimately be traceable from operational transactions through accounting/GL records into FP&A metrics. M1 does not need to implement the complete chain yet, but the base architecture must make the chain possible.

```text
Management Question
    -> KPI / Metric
    -> Comparison Basis
    -> Dimensions
    -> Business Drivers
    -> Operational Transactions
    -> Accounting / GL Flows
    -> FP&A Metric Result
    -> Scenario Ground Truth
    -> Agent Result and Feedback
```

## Target PostgreSQL Logical Schemas

M1 uses PostgreSQL logical schemas to separate enterprise concepts by responsibility.

### master

Relatively stable enterprise entities and reference data.

Target tables:

- `business_units`
- `cost_centres`
- `regions`
- `products`
- `customers`
- `suppliers`
- `employees`
- `accounts`

`employees` must include `employee_id` and organizational relationships such as business unit, cost centre, region, manager, role, and employment status. These relationships support future role-based access, row-level security, governance rules, and audit analysis.

`accounts` represents the base chart-of-accounts concept needed to connect operational activity to accounting and FP&A metrics. M1 is not a complete ERP implementation, but it should preserve the accounting path.

### operations

Business activity and lower-grain operational events.

Target tables:

- `orders`
- `order_lines`
- `invoices`
- `payments`
- `purchases`
- `supplier_invoices`
- `headcount_events`
- `business_events`
- `ai_usage`

This layer contains the evidence that future investigation agents may inspect, subject to policy and access rules. It should support customer activity, supplier cost changes, hiring changes, contractor costs, cloud-cost spikes, marketing spend, FX-sensitive transactions, and CAPEX-related operational events.

`operations.ai_usage` is reserved for later milestones only. It may eventually store application/workflow, business unit, employee/user, model, input/output tokens, estimated model cost, and latency. M1 must not implement AI economics, ROI optimization, or marginal resource allocation optimization.

### finance

Financial and accounting outcomes.

Target tables:

- `journal_entries`
- `actuals`
- `monthly_financials`
- `capex_projects`
- `fixed_assets`
- `depreciation`

The finance layer connects operational transactions to accounting outcomes and FP&A reporting. It should eventually support P&L, CAPEX, and cash-flow investigation without becoming a full ERP or accounting system.

OPEX path:

```text
OPEX -> expense -> EBITDA impact
```

CAPEX path:

```text
CAPEX -> asset / cash outflow -> depreciation or amortisation later -> EBIT impact rather than direct initial EBITDA impact
```

FX should be represented in the base requirements so future questions can explain whether variances come from operational performance, price/volume/mix, timing, or exchange-rate movements.

### planning

Budgets, forecasts, versions, and assumptions.

Target tables:

- `budgets`
- `forecasts`
- `forecast_versions`
- `assumptions`

Planning data provides the comparison basis for FP&A investigation. Versioned forecasts and assumptions are required to distinguish execution problems from planning assumption errors.

### security

Future identity, authorization, row-level security, and audit support.

Target tables:

- `users`
- `roles`
- `user_roles`
- `data_access`
- `audit_log`

M1 designs for this layer but does not implement full RLS enforcement. Future security work must be able to restrict data by employee, role, business unit, cost centre, region, customer, supplier, and sensitivity level.

### evaluation

Permanent evaluation and benchmark schema.

Target tables:

- `scenarios`
- `scenario_ground_truth`
- `investigation_questions`
- `expected_answers`
- `agent_runs`
- `agent_feedback`
- `evaluation_results`

`evaluation.scenario_ground_truth` is evaluator-only. It must never be accessible to the investigation agent. Agents may inspect approved operational evidence such as `operations.business_events`; they must not inspect the injected answer key.

## Current Baseline Components

The current implementation remains a small FastAPI baseline:

- FastAPI exposes `/health`, `/metrics`, and `/ask`.
- PostgreSQL stores synthetic business performance data.
- SQLAlchemy manages database connectivity.
- The semantic layer defines metric names, formulas, synonyms, and allowed dimensions in YAML.
- The AI layer creates CFO-style commentary, with deterministic mock commentary when no OpenAI key is configured.

This baseline is preserved while M1 documentation is refined. This task does not modify runtime code, SQL implementation, Docker configuration, tests, or Python generators.

## Target Enterprise AI Flow

```text
Business Question
    |
API Boundary
    |
Identity / Policy Check
    |
Agent Runtime
    |
Tools / Retrieval / Data
    |
Evaluation / Guardrails
    |
Human Approval
    |
Decision Response
    |
Audit / Tracing / Metrics
```

The platform is not a generic chatbot. It should demonstrate enterprise control points:

- AI reads enterprise data only through approved tools and policy checks.
- Tools analyze governed data sources instead of relying on model memory.
- Answers are validated before becoming decision responses.
- User roles determine which data and actions are available.
- High-risk actions can require human approval.
- Every agent execution can be traced from question to tool calls to final response.
- Cost, latency, reliability, security behavior, and answer quality can be monitored over time.
