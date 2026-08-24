# Architecture

## Purpose

Decision Intelligence Platform Lab models a realistic **B2B SaaS + Professional Services** enterprise so business questions can be investigated from operational evidence through accounting outcomes, FP&A metrics, agent responses, and evaluation feedback.

M1 is **Enterprise Data Foundation + Backend**. Later milestones extend the same platform rather than creating separate demos.

The company has two distinct revenue motions:

1. Recurring SaaS.
2. Professional Services.

They may share customer, commercial, planning, and accounting dimensions, but their operational flows must remain distinct.

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

Revenue Recognition is a **core M1 finance capability**. M1 should support a simplified and explainable recognition model, not a complete IFRS 15 / AASB 15 engine.

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
    -> Business Development / Sales Opportunity
    -> Contract
```

Lead-to-contract is lightweight/supporting in M1.

```text
Customer Contract
    -> Subscription
    -> Subscription Event
    -> Billing
    -> Customer Invoice
    -> Revenue Schedule
    -> Revenue Recognition
    -> Journal / GL
    -> Recognised Revenue
    -> FP&A
```

Subscription events should conceptually support `NEW`, `RENEWAL`, `EXPANSION`, `CONTRACTION`, and `CHURN`.

This flow supports ARR, MRR, New ARR, Expansion ARR, Contraction ARR, Churned ARR, NRR, GRR, billings, deferred revenue, and recognised revenue.

```text
Customer Contract / SOW
    -> Project
    -> Milestone and/or Time Entry
    -> Billing
    -> Revenue Recognition
    -> Journal / GL
    -> Project Revenue
    -> FP&A
```

Professional Services must not be forced into the SaaS subscription model. This flow supports bookings, project revenue, utilisation, billable hours, delivery cost, project margin, and milestones.

```text
Supplier
    -> Purchase
    -> Purchase Line
    -> Supplier Invoice
    -> COGS / OPEX
    -> Journal / GL
```

Procure-to-pay supports supplier pricing, supplier volume, supplier mix, FX, cloud/infrastructure cost, and contractor/vendor cost.

```text
Employee
    -> Headcount / Employment Event
    -> Payroll / People Cost
    -> OPEX
    -> Journal / GL
```

Hire-to-pay supports payroll variance, headcount vs plan, vacancy benefit, hiring delay, salary inflation, and contractor pressure.

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

```text
All Accounting Events
    -> Journal Headers
    -> Journal Lines
    -> GL Accounts
    -> Financial Actuals
    -> FP&A
```

```text
Budget / Forecast
    -> Actual
    -> Variance
    -> Management Question
    -> Agent Investigation
    -> Evaluation / Feedback
```

## Revenue Recognition

Revenue Recognition connects operational commercial data to Accounting / GL and FP&A. M1 should distinguish:

- Bookings.
- ARR / MRR.
- Billings.
- Recognised Revenue.
- Deferred Revenue.
- Cash.

Example:

```text
Annual SaaS contract = 120,000
Invoice = 120,000
Cash received = 120,000
Recognised revenue = 10,000 per month for 12 months
```

Architecture principle:

```text
Bookings != Billings != Revenue != Cash
```

Do not design advanced revenue-recognition edge cases in M1, including complex performance obligations, advanced contract modifications, a full IFRS/AASB accounting engine, or detailed tax treatment.

## Logical Data Areas

The target PostgreSQL architecture preserves the six conceptual enterprise layers:

- `master`: stable enterprise entities and conformed dimensions.
- `operations`: commercial, SaaS, Professional Services, billing, procurement, people, business-event, and FX operational evidence.
- `finance`: revenue schedules, journal headers, journal lines, actuals, CAPEX projects, fixed assets, and depreciation.
- `planning`: budgets, forecasts, forecast versions, and headcount plan.
- `security`: users, roles, user-role assignments, data access rules, and audit logs.
- `evaluation`: scenarios, ground truth, investigation questions, expected answers, agent runs, feedback, and evaluation results.

Business-flow groupings such as Commercial / SaaS, Professional Services, Customer Billing, Procurement, and People describe table families inside the enterprise model. They do not replace the six conceptual layers.

Detailed management-question requirements live in [reference/REQUIREMENTS_TRACEABILITY.md](reference/REQUIREMENTS_TRACEABILITY.md).

Detailed scenario and evaluation design lives in [reference/SCENARIO_MODEL.md](reference/SCENARIO_MODEL.md).

Detailed target table inventory lives in [reference/REQUIREMENTS_TRACEABILITY.md](reference/REQUIREMENTS_TRACEABILITY.md).

## Data Model Principles

- Broad architecture, narrow implementation.
- Use conformed dimensions across operations, finance, and planning.
- Do not force business unit, region, and cost centre into one hierarchy.
- Shared cost centres may have nullable business-unit relationships.
- Keep business dimensions independently joinable.
- Preserve source-transaction references into journal/accounting data.
- Store base facts and drivers; calculate variance and driver measures in transformation or semantic layers where practical.
- Avoid premature shared-cost allocation engines.
- Avoid building a full ERP, CRM, or Professional Services Automation platform.
- Keep the model scalable without over-engineering V1.

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
