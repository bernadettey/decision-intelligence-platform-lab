# Architecture

## Purpose

Decision Intelligence Platform Lab models a realistic B2B technology enterprise so business questions can be investigated from operational evidence through accounting outcomes, FP&A metrics, agent responses, and evaluation feedback.

M1 is **Enterprise Data Foundation + Backend**. Later milestones extend the same platform rather than creating separate demos.

## Synthetic Enterprise

### Commercial

- Business Development.
- Marketing.
- Sales.
- Customer Success.

Commercial activity should connect demand generation, opportunities, orders, invoices, revenue, and customer outcomes.

### Operations / Internal

- Procurement / Suppliers.
- Product / Technology.
- People / HR.

Operational activity should explain supplier cost, delivery capacity, cloud or technology cost, headcount, contractor spend, and other internal drivers.

### Finance

- Accounting / GL.
- FP&A.
- Budget / Forecast.
- CAPEX / Assets.
- Cash Flow.
- FX.

Finance connects operational transactions to actuals, management reporting, planning comparisons, cash and asset effects, and KPI variance analysis.

### Platform

- Security / RLS / Governance.
- Evaluation / Ground Truth / Feedback.
- AI Usage / Economics (future / reserved).

Platform capabilities control access, evaluation, auditability, and future cost/economic analysis without expanding M1 implementation scope.

## Main Enterprise Causal Flow

```text
Business Event
    -> Operational Driver
    -> Operational Transaction
    -> Accounting Event / GL
    -> Financial Actual
    -> FP&A KPI / Variance
    -> Management Question
    -> Agent Investigation
    -> Decision / Action
    -> Evaluation / Feedback
```

Actual financial outcomes should ultimately be traceable from operational transactions through accounting/GL records into FP&A metrics.

## Enterprise Business Flows

```text
Marketing
    -> Lead
    -> BD Opportunity
    -> Sales Order
    -> Customer Invoice
    -> Revenue
    -> GL
    -> FP&A
```

```text
Customer
    -> Order
    -> Order Line
    -> Invoice
    -> Revenue
    -> EBITDA
```

```text
Supplier
    -> Purchase
    -> Supplier Invoice
    -> COGS
    -> Gross Margin
    -> EBITDA
```

```text
Employee
    -> Headcount / Payroll
    -> OPEX
    -> EBITDA
```

```text
CAPEX Project
    -> Asset
    -> Cash Outflow
    -> Depreciation / Amortisation
    -> EBIT / Cash Flow
```

```text
FX
    -> Revenue and/or supplier-cost translation/economic impact
    -> Margin / EBITDA impact
```

## Logical Data Areas

The target PostgreSQL architecture uses logical schemas:

- `master`: stable enterprise entities such as business units, cost centres, regions, products, customers, suppliers, employees, and accounts.
- `operations`: activity and event evidence such as orders, invoices, purchases, supplier invoices, headcount events, business events, and reserved AI usage.
- `finance`: accounting and financial outcomes such as journal entries, actuals, monthly financials, CAPEX projects, fixed assets, and depreciation.
- `planning`: budgets, forecasts, versions, and assumptions.
- `security`: users, roles, user-role assignments, data access rules, and audit logs.
- `evaluation`: scenarios, ground truth, investigation questions, expected answers, agent runs, feedback, and evaluation results.

Detailed management-question requirements live in [reference/REQUIREMENTS_TRACEABILITY.md](reference/REQUIREMENTS_TRACEABILITY.md).

Detailed scenario and evaluation design lives in [reference/SCENARIO_MODEL.md](reference/SCENARIO_MODEL.md).

## Safe Investigation Flow

```text
Management Question
    -> Question Resolution
    -> Capability / Authorization / Data Sufficiency
    -> Evidence-Grounded Investigation
    -> Response
    -> Audit / Evaluation / Feedback
```

Architecture-level principle: the agent should answer only from approved capabilities, authorized data, and sufficient evidence.

Detailed ambiguity, answerability, authorization, and evidence-boundary policy lives in [reference/SECURITY_AND_ANSWERABILITY.md](reference/SECURITY_AND_ANSWERABILITY.md).

## Current Baseline Components

The current implementation remains a small FastAPI baseline:

- FastAPI exposes `/health`, `/metrics`, and `/ask`.
- PostgreSQL stores synthetic business performance data.
- SQLAlchemy manages database connectivity.
- The semantic layer defines metric names, formulas, synonyms, and allowed dimensions in YAML.
- The AI layer creates CFO-style commentary, with deterministic mock commentary when no OpenAI key is configured.

This documentation reorganization does not change runtime code, SQL implementation, Docker configuration, tests, or generators.
