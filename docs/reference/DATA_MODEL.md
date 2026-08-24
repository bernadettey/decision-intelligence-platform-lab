# Logical Data Model v1

## Purpose

This is the authoritative Logical Data Model v1 for M1 PostgreSQL DDL design.

It is documentation only. It does not implement SQL, application code, seed data, tests, Docker configuration, generators, or runtime behavior.

The model preserves the current architecture decisions:

- Synthetic company: **B2B SaaS + Professional Services**.
- SaaS and Professional Services have distinct operational revenue motions.
- Revenue Recognition is M1 CORE.
- Procurement and People are operational driver chains.
- GL/journal is the accounting actual source of truth.
- Planning is separate but uses conformed dimensions.
- `evaluation.scenario_ground_truth` is evaluator-only.
- Answerability/security rules remain in [SECURITY_AND_ANSWERABILITY.md](SECURITY_AND_ANSWERABILITY.md).

## Conceptual Layers

- `master`: conformed dimensions and reference entities.
- `operations`: SaaS, Professional Services, billing, procurement, people, business-event, and FX evidence.
- `finance`: revenue recognition, journal/accounting actuals, CAPEX/assets.
- `planning`: budgets, forecasts, versions, and headcount plan.
- `evaluation`: scenarios and evaluator-only benchmark truth.
- `security`: future M6 identity, authorization, RLS, and audit support.

Future tables may remain documented, but they must not expand M1 implementation scope.

## Source-of-Truth Rules

Operational truth:

- `subscriptions`
- `subscription_events`
- `projects`
- `project_milestones`
- `time_entries`
- `purchases`
- `supplier_invoices`
- `payroll`
- `headcount_events`

Revenue recognition truth:

- `revenue_schedules`

Accounting actual truth:

- `journal_lines`

Planning truth:

- `budgets`
- `forecasts`
- `forecast_versions`

Evaluation truth:

- `evaluation.scenario_ground_truth`
- Evaluator-only. Never agent-visible.

Derived management metrics should generally be calculated in transformation or semantic layers rather than duplicated as source-of-truth columns unless a documented business reason exists:

- ARR.
- MRR.
- NRR.
- GRR.
- Utilisation.
- Project margin.
- EBITDA variance.
- Driver effects.

## Data Model Principles

- Broad architecture, narrow implementation.
- Use conformed dimensions across operations, finance, and planning.
- Do not force business unit, region, and cost centre into one hierarchy.
- Shared cost centres may have nullable business-unit relationships.
- Keep business dimensions independently joinable.
- Preserve source-transaction references into journal/accounting data.
- Store base facts and drivers; calculate variance/driver measures in transformation or semantic layers where practical.
- Avoid premature shared-cost allocation engines.
- Avoid building a full ERP, CRM, or PSA platform.
- Keep the model scalable without over-engineering V1.

## V1.1 Production Metadata Decisions

V1.1 adds a minimal source-system foundation for historical bootstrap generation, incremental synthetic generation, replay, and future ingestion/observability. It does not implement the synthetic generator, CDC infrastructure, pipeline orchestration, Databricks, ADF, Airflow, Kafka, Debezium, agents, ML, or cloud infrastructure.

### Simulation State

`operations.simulation_control` persists generator state between runs:

- `simulation_id`
- `current_simulation_date`
- `last_run_at`
- `random_seed`
- `simulation_speed`
- `run_status`
- `current_batch_id`
- `created_at`
- `updated_at`

Future generator flow:

```text
read current_simulation_date
-> generate next simulation period
-> commit source rows
-> advance simulation state
```

M1.3 Phase 1 intentionally does not drive `simulation_control.run_status`.
`operations.ingestion_batches.status` is the authoritative lifecycle state for
individual generator runs until there is enough generator behavior to justify a
separate simulation-level state machine.

### Batch Lineage

`operations.ingestion_batches` identifies each synthetic generation or replay run:

- `batch_id`
- `simulation_id`
- `simulation_date`
- `batch_type`
- `started_at`
- `completed_at`
- `status`
- `records_generated`
- `generator_version`
- `error_message`

Supported batch types:

- `BOOTSTRAP`
- `INCREMENTAL`
- `REPLAY`

Tables with `ingestion_batch_id` use a foreign key to `operations.ingestion_batches(batch_id)` where this does not create avoidable bootstrap dependency problems.

`generator_version` identifies the version of generator logic that produced the batch. V1.1 stores it as required batch lineage with a transitional default for manual bootstrap data, so future runs can be reproduced and debugged using `simulation_date`, `random_seed`, and `generator_version`.

### Audit Timestamps

Audit metadata is added selectively, not mechanically. Operational mutable and transactional tables receive:

- `created_at`
- `updated_at`
- `source_system`
- `ingestion_batch_id`

Finance lineage tables receive source/batch metadata appropriate to accounting traceability:

- `finance.revenue_schedules`
- `finance.journal_headers`
- `finance.journal_lines`

Reference/master tables remain simple unless they are mutable operational dimensions. `master.employees` receives audit and CDC-ready metadata because employee records change over time and support future governance/RLS.

### CDC Readiness

`record_version` and `is_deleted` are added only to records likely to be updated by future source simulation:

- `master.employees`
- `operations.customer_contracts`
- `operations.subscriptions`
- `operations.projects`
- `operations.project_milestones`
- `operations.customer_invoices`
- `operations.purchases`
- `operations.supplier_invoices`

Append-style events and accounting facts do not receive deletion semantics. In particular, journals must remain append/reversal oriented. Do not model journal deletion with `is_deleted`.

### Event Time vs Ingestion Time

Business/event time describes when the business event happened:

- `event_date`
- `invoice_date`
- `entry_date`
- `period`
- `recognition_period`

System/source lifecycle time describes when a source record was created or updated:

- `created_at`
- `updated_at`

Batch ingestion time describes when generation or ingestion ran:

- `ingestion_batches.started_at`
- `ingestion_batches.completed_at`

Do not use ingestion timestamps as substitutes for business dates.

### Future Watermarks

V1.1 does not add a watermark service or ingestion pipeline. The schema is ready for later patterns such as:

```text
updated_at > last_successful_watermark
```

or:

```text
ingestion_batch_id > last_processed_batch
```

Watermark state, MERGE/upsert logic, and transformation-layer replay handling belong to later ingestion/transformation work.

### Idempotency and Replay Principles

- Deterministic business keys or stable primary keys should prevent duplicate synthetic records.
- `batch_id` identifies the generation run that produced source rows.
- `random_seed` makes synthetic generation reproducible.
- `generator_version` identifies which generator logic produced a batch.
- `REPLAY` batches must be distinguishable from normal `INCREMENTAL` batches.
- Future ingestion should be rerunnable without duplicating downstream facts.
- MERGE/upsert behavior belongs to later ingestion/transformation layers, not this source PostgreSQL implementation.

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
| PEOPLE | `headcount_events` | CORE |
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
| OPERATIONS CONTROL | `simulation_control` | V1.1 CORE |
| OPERATIONS CONTROL | `ingestion_batches` | V1.1 CORE |
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

## Core Table Specifications

### MASTER

#### `business_units`

- Purpose: Conformed commercial/operating business unit dimension.
- Grain: One row per business unit.
- Primary key: `business_unit_id`.
- Foreign keys: None required in V1.
- Minimum attributes: `business_unit_id`, `business_unit_name`, `active_flag`.
- Nullable decisions: None.
- Important constraints: Business unit name should be unique.
- Lineage role: Dimension used across operations, finance, planning, security, and evaluation.
- Supports: Business-unit variance, ARR, recognised revenue, OPEX, EBITDA, and scenario analysis.

#### `regions`

- Purpose: Conformed geography/market dimension.
- Grain: One row per region.
- Primary key: `region_id`.
- Foreign keys: None required in V1.
- Minimum attributes: `region_id`, `region_name`, `active_flag`.
- Nullable decisions: None.
- Important constraints: Region name should be unique.
- Lineage role: Geography dimension for operations, planning, security, and evaluation.
- Supports: Regional ARR, revenue, COGS, FX, payroll, and margin investigation.

#### `departments`

- Purpose: Functional organization dimension.
- Grain: One row per department.
- Primary key: `department_id`.
- Foreign keys: None required in V1.
- Minimum attributes: `department_id`, `department_name`, `active_flag`.
- Nullable decisions: None.
- Important constraints: Department name should be unique.
- Lineage role: People, OPEX, payroll, and headcount planning dimension.
- Supports: OPEX variance, headcount vs plan, payroll variance.

#### `cost_centres`

- Purpose: Cost ownership and planning dimension.
- Grain: One row per cost centre.
- Primary key: `cost_centre_id`.
- Foreign keys: `business_unit_id` nullable to `business_units.business_unit_id`; `department_id` nullable to `departments.department_id`; `manager_employee_id` nullable to `employees.employee_id`.
- Minimum attributes: `cost_centre_id`, `cost_centre_name`, `business_unit_id`, `department_id`, `manager_employee_id`, `active_flag`.
- Nullable decisions: `business_unit_id` may be null for shared cost centres. `manager_employee_id` must be nullable because of the employees/cost-centres seed cycle.
- Important constraints: Cost centre name should be unique within relevant organization context.
- Lineage role: Conformed OPEX, payroll, planning, and security dimension.
- Supports: OPEX variance, shared-cost analysis, headcount planning, RLS/governance.

Known logical cycle:

```text
employees.cost_centre_id -> cost_centres.cost_centre_id
cost_centres.manager_employee_id -> employees.employee_id
```

`manager_employee_id` must be nullable.

Expected seed order:

1. Create cost centre with manager `NULL`.
2. Create employees.
3. Update `manager_employee_id`.

Do not introduce extra tables solely to remove this V1 logical cycle.

#### `customers`

- Purpose: Customer/account dimension shared by SaaS and Professional Services.
- Grain: One row per customer.
- Primary key: `customer_id`.
- Foreign keys: `region_id` to `regions.region_id`; optional `business_unit_id` to `business_units.business_unit_id`.
- Minimum attributes: `customer_id`, `customer_name`, `region_id`, `business_unit_id`, `customer_segment`, `active_flag`.
- Nullable decisions: `business_unit_id` may be nullable if customer ownership is shared or assigned later.
- Important constraints: Customer name should be unique enough for synthetic data; customer segment controlled by documented values.
- Lineage role: Root entity for contracts, subscriptions, projects, billing, revenue, and churn.
- Supports: Customer revenue, churned ARR, recognised revenue, project revenue, deferred revenue.

#### `products`

- Purpose: Product/SKU dimension for SaaS and related commercial analysis.
- Grain: One row per product.
- Primary key: `product_id`.
- Foreign keys: Optional `business_unit_id` to `business_units.business_unit_id`.
- Minimum attributes: `product_id`, `product_name`, `product_family`, `business_unit_id`, `active_flag`.
- Nullable decisions: `business_unit_id` may be null for shared products.
- Important constraints: Product name should be unique.
- Lineage role: Product-level ARR, revenue, pricing, and margin dimension.
- Supports: Product mix, ARR movement, recognised revenue, gross margin.

#### `suppliers`

- Purpose: Supplier/vendor dimension.
- Grain: One row per supplier.
- Primary key: `supplier_id`.
- Foreign keys: Optional `region_id` to `regions.region_id`; optional `currency_code` to `currencies.currency_code`.
- Minimum attributes: `supplier_id`, `supplier_name`, `supplier_category`, `region_id`, `currency_code`, `active_flag`.
- Nullable decisions: Region may be null when supplier geography is not relevant.
- Important constraints: Supplier name should be unique enough for synthetic data.
- Lineage role: Root for procurement, supplier invoices, cloud/vendor costs, FX exposure.
- Supports: Supplier price, volume, mix, COGS/OPEX, FX, contractor/vendor cost.

#### `employees`

- Purpose: Employee dimension for people cost, project delivery, management, and future governance.
- Grain: One row per employee.
- Primary key: `employee_id`.
- Foreign keys: `cost_centre_id` to `cost_centres.cost_centre_id`; optional `business_unit_id`, `region_id`, `department_id`; optional `manager_employee_id` self-reference.
- Minimum attributes: `employee_id`, `employee_name`, `role_title`, `business_unit_id`, `region_id`, `department_id`, `cost_centre_id`, `manager_employee_id`, `employment_status`, `start_date`, `end_date`.
- Nullable decisions: `manager_employee_id` nullable for top-level managers. `end_date` nullable for active employees.
- Important constraints: Employee must have a cost centre in V1 if used for payroll/time entries.
- Lineage role: People, payroll, project delivery cost, RLS/governance dimension.
- Supports: Payroll variance, headcount vs plan, utilisation, delivery cost, employee/role-based access.

#### `gl_accounts`

- Purpose: Chart of accounts dimension.
- Grain: One row per GL account.
- Primary key: `gl_account_id`.
- Foreign keys: None required in V1.
- Minimum attributes: `gl_account_id`, `account_code`, `account_name`, `account_type`, `normal_balance`, `active_flag`.
- Nullable decisions: None.
- Important constraints: `account_code` should be unique. `account_type` should use controlled values such as revenue, COGS, OPEX, asset, liability, equity.
- Lineage role: Required accounting dimension for journal lines and planning facts.
- Supports: P&L, deferred revenue, cash, CAPEX/assets, EBITDA/EBIT analysis.

#### `currencies`

- Purpose: Currency reference dimension.
- Grain: One row per currency.
- Primary key: `currency_code`.
- Foreign keys: None.
- Minimum attributes: `currency_code`, `currency_name`, `active_flag`.
- Nullable decisions: None.
- Important constraints: ISO-like currency codes should be unique.
- Lineage role: Currency reference for transactions, FX rates, invoices, and journals.
- Supports: FX-sensitive revenue, supplier cost, cash, and margin investigation.

### COMMERCIAL / SAAS

#### `customer_contracts`

- Purpose: Contract root shared by SaaS subscriptions and Professional Services projects/SOWs.
- Grain: One row per customer contract or SOW.
- Primary key: `contract_id`.
- Foreign keys: `customer_id`, optional `business_unit_id`, `region_id`, `currency_code`.
- Minimum attributes: `contract_id`, `customer_id`, `contract_type`, `contract_start_date`, `contract_end_date`, `contract_value`, `currency_code`, `business_unit_id`, `region_id`, `contract_status`.
- Nullable decisions: End date may be nullable for open-ended service relationships, but SaaS contract terms should generally have start/end.
- Important constraints: `contract_type` should distinguish SaaS, Professional Services, or mixed contract.
- Lineage role: Commercial source for subscriptions, projects, billing, and revenue schedules.
- Supports: Bookings, ARR, billings, recognised revenue, project revenue, customer contract delay.

#### `subscriptions`

- Purpose: SaaS recurring revenue operational model.
- Grain: One row per customer/product subscription.
- Primary key: `subscription_id`.
- Foreign keys: `contract_id`, `customer_id`, `product_id`, optional `business_unit_id`, `region_id`.
- Minimum attributes: `subscription_id`, `contract_id`, `customer_id`, `product_id`, `start_date`, `end_date`, `billing_frequency`, `arr_amount`, `mrr_amount`, `subscription_status`.
- Nullable decisions: End date may be nullable for active subscriptions until churn/termination is known.
- Important constraints: Subscription must belong to a contract and customer.
- Lineage role: Operational truth for recurring SaaS base.
- Supports: ARR, MRR, NRR, GRR, churned ARR, expansion/contraction analysis.

#### `subscription_events`

- Purpose: SaaS ARR movement event log.
- Grain: One row per subscription event.
- Primary key: `subscription_event_id`.
- Foreign keys: `subscription_id`, `customer_id`, optional `product_id`.
- Minimum attributes: `subscription_event_id`, `subscription_id`, `customer_id`, `event_date`, `event_type`, `arr_delta`, `mrr_delta`, `event_reason`.
- Nullable decisions: `product_id` may be nullable if the event applies to the full subscription.
- Important constraints: `event_type` must support `NEW`, `RENEWAL`, `EXPANSION`, `CONTRACTION`, `CHURN`.
- Lineage role: Operational truth for ARR movement.
- Supports: ARR bridge, churned ARR, expansion ARR, contraction ARR, NRR/GRR.

### PROFESSIONAL SERVICES

#### `projects`

- Purpose: Professional Services delivery model, distinct from SaaS subscriptions.
- Grain: One row per customer project/SOW.
- Primary key: `project_id`.
- Foreign keys: `contract_id`, `customer_id`, optional `business_unit_id`, `region_id`, `currency_code`.
- Minimum attributes: `project_id`, `contract_id`, `customer_id`, `project_name`, `project_status`, `start_date`, `end_date`, `contracted_amount`, `currency_code`.
- Nullable decisions: End date may be nullable for active projects.
- Important constraints: Project must not be modeled as a subscription.
- Lineage role: Operational truth for Professional Services revenue and delivery.
- Supports: Project revenue, milestone timing, utilisation, billable hours, delivery cost, project margin.

#### `project_milestones`

- Purpose: Milestone plan/progress for service delivery and revenue recognition support.
- Grain: One row per project milestone.
- Primary key: `milestone_id`.
- Foreign keys: `project_id`.
- Minimum attributes: `milestone_id`, `project_id`, `milestone_name`, `planned_date`, `actual_date`, `milestone_amount`, `milestone_status`.
- Nullable decisions: `actual_date` nullable until completed.
- Important constraints: Milestone belongs to exactly one project.
- Lineage role: Operational delivery evidence for project timing and revenue recognition.
- Supports: Milestone delay, project revenue miss, recognised revenue timing.

#### `time_entries`

- Purpose: Employee time/cost evidence for Professional Services delivery.
- Grain: One row per employee/project/date time entry.
- Primary key: `time_entry_id`.
- Foreign keys: `project_id`, `employee_id`.
- Minimum attributes: `time_entry_id`, `project_id`, `employee_id`, `entry_date`, `hours`, `billable_flag`, `hourly_cost_rate`, `hourly_bill_rate`.
- Nullable decisions: `hourly_bill_rate` may be null for non-billable time.
- Important constraints: Hours must be non-negative.
- Lineage role: Operational source for utilisation, billable hours, and delivery cost.
- Supports: Utilisation, billable hours, project margin, delivery cost above plan.

### CUSTOMER BILLING

#### `customer_invoices`

- Purpose: Customer billing header shared by SaaS and Professional Services.
- Grain: One row per customer invoice.
- Primary key: `customer_invoice_id`.
- Foreign keys: `customer_id`, `currency_code`, optional `contract_id`.
- Minimum attributes: `customer_invoice_id`, `customer_id`, `contract_id`, `invoice_date`, `due_date`, `currency_code`, `invoice_status`, `invoice_total`.
- Nullable decisions: `contract_id` may be nullable for miscellaneous invoice types.
- Important constraints: Invoice total should reconcile to invoice lines in generated data.
- Lineage role: Billing source before cash and revenue recognition.
- Supports: Billings, deferred revenue, cash timing, revenue-recognition timing.

#### `customer_invoice_lines`

- Purpose: Customer invoice detail with source-motion integrity.
- Grain: One row per invoice line.
- Primary key: `customer_invoice_line_id`.
- Foreign keys: `customer_invoice_id`; nullable `subscription_id`; nullable `project_id`; optional `gl_account_id`.
- Minimum attributes: `customer_invoice_line_id`, `customer_invoice_id`, `source_type`, `subscription_id`, `project_id`, `line_amount`, `currency_code`, `description`.
- Nullable decisions: `subscription_id` and `project_id` depend on `source_type`.
- Important constraints:
  - `source_type = SUBSCRIPTION`: `subscription_id` not null and `project_id` null.
  - `source_type = PROJECT`: `project_id` not null and `subscription_id` null.
  - `source_type = OTHER`: both may be null according to documented V1 rules.
- Lineage role: Shared billing infrastructure while preserving SaaS vs Services semantics.
- Supports: Billings, SaaS revenue, project revenue, deferred revenue.

#### `customer_payments` SUPPORT

- Purpose: Customer cash collection support.
- Grain: One row per customer payment.
- Primary key: `customer_payment_id`.
- Foreign keys: `customer_invoice_id`, `customer_id`, `currency_code`.
- Minimum attributes: `customer_payment_id`, `customer_invoice_id`, `customer_id`, `payment_date`, `payment_amount`, `currency_code`.
- Nullable decisions: None for linked invoice payments.
- Important constraints: Payment amount should be non-negative.
- Lineage role: Cash evidence, not revenue truth.
- Supports: Cash vs billings vs revenue distinction.

### PROCUREMENT

#### `purchases`

- Purpose: Purchase header for supplier procurement.
- Grain: One row per purchase/order.
- Primary key: `purchase_id`.
- Foreign keys: `supplier_id`, optional `business_unit_id`, `region_id`, `cost_centre_id`, `currency_code`.
- Minimum attributes: `purchase_id`, `supplier_id`, `purchase_date`, `currency_code`, `purchase_status`, `business_unit_id`, `region_id`, `cost_centre_id`.
- Nullable decisions: Business unit and cost centre may be nullable for shared procurement.
- Important constraints: Purchase belongs to one supplier.
- Lineage role: Operational procurement evidence.
- Supports: Supplier volume, supplier mix, cloud/vendor cost, contractor/vendor cost.

#### `purchase_lines`

- Purpose: Purchase detail.
- Grain: One row per purchase line.
- Primary key: `purchase_line_id`.
- Foreign keys: `purchase_id`, optional `product_id`, optional `gl_account_id`.
- Minimum attributes: `purchase_line_id`, `purchase_id`, `item_description`, `quantity`, `unit_price`, `line_amount`, `currency_code`, `gl_account_id`.
- Nullable decisions: `product_id` may be null for services/vendor spend.
- Important constraints: Quantity and amounts should be non-negative unless explicitly modeled otherwise.
- Lineage role: Operational detail for supplier price/volume/mix.
- Supports: Supplier pricing, volume, mix, COGS/OPEX classification.

#### `supplier_invoices`

- Purpose: Supplier invoice header.
- Grain: One row per supplier invoice.
- Primary key: `supplier_invoice_id`.
- Foreign keys: `supplier_id`, optional `purchase_id`, `currency_code`.
- Minimum attributes: `supplier_invoice_id`, `supplier_id`, `purchase_id`, `invoice_date`, `due_date`, `currency_code`, `invoice_total`, `invoice_status`.
- Nullable decisions: `purchase_id` may be nullable for non-PO invoices.
- Important constraints: Invoice total should reconcile to supplier invoice lines in generated data.
- Lineage role: Source for supplier-cost accounting journal entries.
- Supports: COGS/OPEX variance, supplier price changes, FX impacts.

#### `supplier_invoice_lines`

- Purpose: Supplier invoice detail.
- Grain: One row per supplier invoice line.
- Primary key: `supplier_invoice_line_id`.
- Foreign keys: `supplier_invoice_id`, optional `purchase_line_id`, `gl_account_id`.
- Minimum attributes: `supplier_invoice_line_id`, `supplier_invoice_id`, `purchase_line_id`, `gl_account_id`, `line_amount`, `currency_code`, `description`.
- Nullable decisions: `purchase_line_id` nullable for non-PO invoices.
- Important constraints: Must map to a GL account for accounting classification.
- Lineage role: Source detail for COGS/OPEX accounting.
- Supports: Supplier price/volume/mix, cloud cost, contractor/vendor cost.

### PEOPLE

#### `payroll`

- Purpose: Payroll/personnel cost fact.
- Grain: One row per employee per pay period or month.
- Primary key: `payroll_id`.
- Foreign keys: `employee_id`, `cost_centre_id`, optional `business_unit_id`, `region_id`, `gl_account_id`, `currency_code`.
- Minimum attributes: `payroll_id`, `employee_id`, `period`, `cost_centre_id`, `salary_amount`, `bonus_amount`, `benefits_amount`, `total_payroll_cost`, `currency_code`, `gl_account_id`.
- Nullable decisions: Business unit and region may be denormalized from employee and nullable only if employee mapping is incomplete in seed design.
- Important constraints: Period and employee required.
- Lineage role: Operational people-cost truth before journal posting.
- Supports: Payroll variance, salary inflation, OPEX, EBITDA impact.

#### `headcount_events`

- Purpose: Employment event log.
- Grain: One row per employee headcount event.
- Primary key: `headcount_event_id`.
- Foreign keys: `employee_id`, optional `cost_centre_id`, `business_unit_id`, `region_id`.
- Minimum attributes: `headcount_event_id`, `employee_id`, `event_date`, `event_type`, `cost_centre_id`, `business_unit_id`, `region_id`, `fte_change`.
- Nullable decisions: Some organizational dimensions may be nullable if inferred from employee.
- Important constraints: Event type should use controlled values such as hire, termination, transfer, salary_change.
- Lineage role: Operational truth for headcount changes.
- Supports: Headcount vs plan, vacancy benefit, hiring delay, salary inflation.

### FINANCE

#### `revenue_schedules`

- Purpose: Recognised-revenue source before journal posting.
- Grain: One row per revenue recognition schedule line per source and recognition period.
- Primary key: `revenue_schedule_id`.
- Foreign keys: Nullable `subscription_id`; nullable `project_id`; optional `customer_invoice_line_id`; `customer_id`; `gl_account_id`.
- Minimum attributes: `revenue_schedule_id`, `revenue_source_type`, `subscription_id`, `project_id`, `customer_invoice_line_id`, `customer_id`, `recognition_period`, `scheduled_amount`, `recognised_amount`, `currency_code`, `gl_account_id`, `recognition_status`.
- Nullable decisions: `subscription_id` and `project_id` depend on `revenue_source_type`.
- Important constraints:
  - `revenue_source_type = SUBSCRIPTION`: `subscription_id` not null and `project_id` null.
  - `revenue_source_type = PROJECT`: `project_id` not null and `subscription_id` null.
- Lineage role: Revenue recognition truth before journal posting. Do not duplicate recognised-revenue truth in subscriptions or project milestones.
- Supports: Recognised revenue, deferred revenue, recognition timing, EBITDA impact.

#### `journal_headers`

- Purpose: Accounting journal header with polymorphic source lineage.
- Grain: One row per accounting journal.
- Primary key: `journal_header_id`.
- Foreign keys: Optional `currency_code`.
- Minimum attributes: `journal_header_id`, `journal_date`, `period`, `source_type`, `source_id`, `description`, `currency_code`, `posted_flag`.
- Nullable decisions: `source_id` may be nullable only for manual/future unsupported journal types if documented; M1 generated journals should populate it.
- Important constraints: Posted journals should have balancing journal lines in generated data.
- Lineage role: Links journal entries to source systems using V1 polymorphic lineage.
- Supports: Operational-to-accounting traceability.

V1 journal lineage uses:

```text
journal_headers.source_type
journal_headers.source_id
```

Supported V1 source types include:

- `REVENUE_SCHEDULE`
- `SUPPLIER_INVOICE`
- `PAYROLL`

Future source types may be added for accounting sources such as depreciation or cash receipts.

PostgreSQL cannot enforce a normal foreign key from `source_id` to multiple possible source tables. V1 source existence and integrity must be validated by the synthetic-data generator/application layer.

Do not introduce `accounting_events` in V1. `accounting_events` is a possible future hardening path only.

#### `journal_lines`

- Purpose: Accounting actual source of truth.
- Grain: One row per journal debit or credit line.
- Primary key: `journal_line_id`.
- Foreign keys: `journal_header_id`, `gl_account_id`, optional conformed dimensions.
- Minimum attributes: `journal_line_id`, `journal_header_id`, `gl_account_id`, `period`, `debit_amount`, `credit_amount`, `net_amount`, `currency_code`, `business_unit_id`, `region_id`, `cost_centre_id`, `customer_id`, `supplier_id`, `employee_id`, `project_id`, `subscription_id`.
- Nullable decisions: Conformed dimensions may be nullable when not relevant to the journal line.
- Important constraints: Debit/credit conventions should be documented and generated consistently.
- Lineage role: Accounting actual truth for financial results.
- Supports: Actuals, recognised revenue, COGS, OPEX, EBITDA, EBIT, variance analysis.

#### `capex_projects` SUPPORT

- Purpose: CAPEX project support record.
- Grain: One row per CAPEX project.
- Primary key: `capex_project_id`.
- Foreign keys: Optional `business_unit_id`, `region_id`, `cost_centre_id`, `currency_code`.
- Minimum attributes: `capex_project_id`, `project_name`, `planned_start_date`, `planned_in_service_date`, `actual_in_service_date`, `budget_amount`, `actual_amount`, `currency_code`, `project_status`.
- Nullable decisions: Actual in-service date nullable until placed in service.
- Important constraints: Support only; do not build a full asset-management system in M1.
- Lineage role: CAPEX timing and cash-flow support.
- Supports: CAPEX delay, CAPEX overspend, cash-flow and depreciation timing.

#### `fixed_assets` SUPPORT

- Purpose: Fixed asset support record.
- Grain: One row per asset.
- Primary key: `fixed_asset_id`.
- Foreign keys: Optional `capex_project_id`, optional `gl_account_id`.
- Minimum attributes: `fixed_asset_id`, `capex_project_id`, `asset_name`, `in_service_date`, `asset_cost`, `useful_life_months`, `depreciation_method`.
- Nullable decisions: `capex_project_id` nullable for assets not tied to a project in synthetic data.
- Important constraints: Support only; depreciation detail may be simplified.
- Lineage role: Asset/depreciation support for EBIT and cash-flow analysis.
- Supports: CAPEX/assets, depreciation timing, EBIT impact.

### PLANNING

#### `budgets`

- Purpose: Financial budget fact.
- Grain: One row per planning period, GL account, version/snapshot, and applicable planning dimensions.
- Primary key: `budget_id`.
- Foreign keys: `gl_account_id`; nullable `business_unit_id`, `region_id`, `cost_centre_id`; optional `currency_code`.
- Minimum attributes: `budget_id`, `period`, `gl_account_id`, `business_unit_id`, `region_id`, `cost_centre_id`, `budget_amount`, `currency_code`.
- Nullable decisions: Business unit, region, and cost centre may be nullable when budget exists at a higher planning grain.
- Important constraints: `gl_account_id` and `period` required. Do not generate fake dimension members to satisfy not-null planning constraints.
- Lineage role: Planning truth for budget comparisons.
- Supports: Actual vs budget, EBITDA variance, OPEX variance, recognised revenue miss.

#### `forecasts`

- Purpose: Financial forecast fact.
- Grain: One row per forecast version, period, GL account, and applicable planning dimensions.
- Primary key: `forecast_id`.
- Foreign keys: `forecast_version_id`, `gl_account_id`; nullable `business_unit_id`, `region_id`, `cost_centre_id`; optional `currency_code`.
- Minimum attributes: `forecast_id`, `forecast_version_id`, `period`, `gl_account_id`, `business_unit_id`, `region_id`, `cost_centre_id`, `forecast_amount`, `currency_code`.
- Nullable decisions: Business unit, region, and cost centre may be nullable when forecast exists at a higher grain.
- Important constraints: `forecast_version_id`, `gl_account_id`, and `period` required.
- Lineage role: Planning truth for forecast comparisons.
- Supports: Actual vs forecast, recognised revenue forecast miss, margin/EBITDA analysis.

#### `forecast_versions`

- Purpose: Forecast version metadata.
- Grain: One row per forecast version.
- Primary key: `forecast_version_id`.
- Foreign keys: None required in V1.
- Minimum attributes: `forecast_version_id`, `version_name`, `created_at`, `forecast_cutoff_date`, `status`.
- Nullable decisions: None.
- Important constraints: Version name should be unique.
- Lineage role: Planning version control.
- Supports: Current forecast vs prior forecast, assumption/timing analysis.

#### `headcount_plan`

- Purpose: Workforce planning fact.
- Grain: One row per period and applicable organization dimensions.
- Primary key: `headcount_plan_id`.
- Foreign keys: Nullable `business_unit_id`, `region_id`, `department_id`, `cost_centre_id`.
- Minimum attributes: `headcount_plan_id`, `period`, `business_unit_id`, `region_id`, `department_id`, `cost_centre_id`, `planned_fte`, `planned_payroll_cost`.
- Nullable decisions: Dimensions may be nullable when plan exists at a higher grain.
- Important constraints: Period required.
- Lineage role: People planning truth.
- Supports: Headcount vs plan, vacancy benefit, payroll variance.

Planning grain rule:

- Actual may exist at a finer grain.
- Actual must be aggregated to the relevant planning grain before variance comparison.
- Do not force budget/forecast to always have the same detailed grain as actual.
- Do not generate fake dimension members merely to satisfy a NOT NULL planning constraint.

### REFERENCE / OPERATIONS

#### `business_events`

- Purpose: Agent-visible business evidence.
- Grain: One row per business event.
- Primary key: `business_event_id`.
- Foreign keys: Optional conformed dimensions and entity links.
- Minimum attributes: `business_event_id`, `event_date`, `event_type`, `event_description`, `business_unit_id`, `region_id`, `customer_id`, `supplier_id`, `employee_id`, `project_id`, `subscription_id`, `severity`.
- Nullable decisions: Entity links nullable depending on event type.
- Important constraints: Must not contain evaluator-only answer keys.
- Lineage role: Agent-visible evidence for investigation.
- Supports: Root-cause investigation, scenario evidence, management explanations.

#### `fx_rates`

- Purpose: FX reference rates.
- Grain: One row per rate date and currency pair.
- Primary key: `fx_rate_id`.
- Foreign keys: `from_currency_code` and `to_currency_code` to `currencies.currency_code`.
- Minimum attributes: `fx_rate_id`, `rate_date`, `from_currency_code`, `to_currency_code`, `exchange_rate`.
- Nullable decisions: None.
- Important constraints: Currency pair and rate date should be unique.
- Lineage role: FX translation/economic impact reference.
- Supports: FX-sensitive revenue, supplier cost, cash, and margin analysis.

### EVALUATION

#### `scenarios`

- Purpose: Scenario registry.
- Grain: One row per controlled scenario.
- Primary key: `scenario_id`.
- Foreign keys: Optional conformed dimensions.
- Minimum attributes: `scenario_id`, `scenario_type`, `scenario_name`, `period`, `severity`, `active_flag`.
- Nullable decisions: Affected dimensions nullable depending on scenario.
- Important constraints: Scenario type should use controlled values.
- Lineage role: Evaluation scenario root.
- Supports: Scenario-driven tests and benchmark questions.

#### `scenario_ground_truth`

- Purpose: Evaluator-only known truth and causal chain.
- Grain: One row per scenario truth record.
- Primary key: `scenario_ground_truth_id`.
- Foreign keys: `scenario_id`.
- Minimum attributes: `scenario_ground_truth_id`, `scenario_id`, `primary_root_cause`, `expected_driver`, `expected_financial_impact`, `expected_kpi_impact`, `expected_causal_chain`.
- Nullable decisions: None for core truth fields.
- Important constraints: Evaluator-only; never available to investigation agents.
- Lineage role: Evaluation truth, not operational evidence.
- Supports: Root-cause accuracy, evidence grounding, answerability checks.

#### `investigation_questions`

- Purpose: Benchmark management questions.
- Grain: One row per scenario question.
- Primary key: `investigation_question_id`.
- Foreign keys: `scenario_id`.
- Minimum attributes: `investigation_question_id`, `scenario_id`, `question_text`, `persona`, `expected_answerability`, `ambiguity_behavior`.
- Nullable decisions: Persona may be nullable for generic evaluation questions.
- Important constraints: Must not expose ground truth in question text.
- Lineage role: Evaluation input for agents.
- Supports: Agent benchmarks, answerability, ambiguity handling.

#### `expected_answers`

- Purpose: Expected response criteria.
- Grain: One row per investigation question expected answer.
- Primary key: `expected_answer_id`.
- Foreign keys: `investigation_question_id`, `scenario_id`.
- Minimum attributes: `expected_answer_id`, `investigation_question_id`, `scenario_id`, `required_root_cause`, `required_evidence`, `required_kpi_impact`, `unsupported_claims`.
- Nullable decisions: Unsupported claims may be nullable when not relevant.
- Important constraints: Evaluator-only for scoring; not agent-visible during investigation.
- Lineage role: Evaluation criteria.
- Supports: Answer scoring and regression evaluation.

## Future Tables

Future documented tables must not expand M1 implementation scope:

- `agent_runs` M2+.
- `agent_feedback` M2+.
- `evaluation_results` M7.
- `users`, `roles`, `user_roles`, `data_access`, `audit_log` M6.
- `ai_usage` future AI economics only.

## Relationship Matrix

| From table | FK | To table | Notes |
| --- | --- | --- | --- |
| `cost_centres` | `business_unit_id` | `business_units` | Nullable for shared cost centres. |
| `cost_centres` | `department_id` | `departments` | Nullable when not department-specific. |
| `cost_centres` | `manager_employee_id` | `employees` | Nullable; see circular dependency decision. |
| `customers` | `region_id` | `regions` | Customer geography. |
| `customers` | `business_unit_id` | `business_units` | Nullable for shared ownership. |
| `products` | `business_unit_id` | `business_units` | Nullable for shared products. |
| `suppliers` | `region_id` | `regions` | Nullable. |
| `suppliers` | `currency_code` | `currencies` | Supplier default currency. |
| `employees` | `cost_centre_id` | `cost_centres` | Required when employee is used in facts. |
| `employees` | `business_unit_id` | `business_units` | Organization relationship. |
| `employees` | `region_id` | `regions` | Organization relationship. |
| `employees` | `department_id` | `departments` | Organization relationship. |
| `employees` | `manager_employee_id` | `employees` | Nullable self-reference. |
| `customer_contracts` | `customer_id` | `customers` | Contract root. |
| `subscriptions` | `contract_id` | `customer_contracts` | SaaS path. |
| `subscriptions` | `customer_id` | `customers` | Denormalized for join convenience. |
| `subscriptions` | `product_id` | `products` | SaaS product. |
| `subscription_events` | `subscription_id` | `subscriptions` | ARR movement. |
| `projects` | `contract_id` | `customer_contracts` | Professional Services path. |
| `projects` | `customer_id` | `customers` | Project customer. |
| `project_milestones` | `project_id` | `projects` | Delivery milestone. |
| `time_entries` | `project_id` | `projects` | Delivery effort. |
| `time_entries` | `employee_id` | `employees` | Delivery employee. |
| `customer_invoices` | `customer_id` | `customers` | Billing header. |
| `customer_invoice_lines` | `customer_invoice_id` | `customer_invoices` | Billing line. |
| `customer_invoice_lines` | `subscription_id` | `subscriptions` | Nullable; constrained by `source_type`. |
| `customer_invoice_lines` | `project_id` | `projects` | Nullable; constrained by `source_type`. |
| `customer_payments` | `customer_invoice_id` | `customer_invoices` | Cash collection. |
| `purchases` | `supplier_id` | `suppliers` | Procurement header. |
| `purchase_lines` | `purchase_id` | `purchases` | Procurement line. |
| `supplier_invoices` | `supplier_id` | `suppliers` | Supplier invoice header. |
| `supplier_invoices` | `purchase_id` | `purchases` | Nullable for non-PO invoices. |
| `supplier_invoice_lines` | `supplier_invoice_id` | `supplier_invoices` | Supplier invoice line. |
| `supplier_invoice_lines` | `purchase_line_id` | `purchase_lines` | Nullable for non-PO invoice lines. |
| `payroll` | `employee_id` | `employees` | Payroll employee. |
| `payroll` | `cost_centre_id` | `cost_centres` | People cost ownership. |
| `headcount_events` | `employee_id` | `employees` | Employment event. |
| `revenue_schedules` | `subscription_id` | `subscriptions` | Nullable; constrained by `revenue_source_type`. |
| `revenue_schedules` | `project_id` | `projects` | Nullable; constrained by `revenue_source_type`. |
| `revenue_schedules` | `customer_invoice_line_id` | `customer_invoice_lines` | Optional billing lineage. |
| `journal_lines` | `journal_header_id` | `journal_headers` | Accounting actual line. |
| `journal_lines` | `gl_account_id` | `gl_accounts` | Required. |
| `budgets` | `gl_account_id` | `gl_accounts` | Required planning account. |
| `forecasts` | `forecast_version_id` | `forecast_versions` | Required forecast version. |
| `forecasts` | `gl_account_id` | `gl_accounts` | Required planning account. |
| `headcount_plan` | organization dimensions | conformed dimensions | Nullable by planning grain. |
| `scenario_ground_truth` | `scenario_id` | `scenarios` | Evaluator-only. |
| `investigation_questions` | `scenario_id` | `scenarios` | Evaluation input. |
| `expected_answers` | `investigation_question_id` | `investigation_questions` | Evaluator-only criteria. |
| `ingestion_batches` | `simulation_id` | `simulation_control` | Generation run belongs to one simulation. |
| `simulation_control` | `current_batch_id` | `ingestion_batches` | Nullable current batch pointer for bootstrap ordering. |
| selected source tables | `ingestion_batch_id` | `ingestion_batches` | Batch lineage where FK-enforced. |

## Logical ERD

```text
customers
    -> customer_contracts
        -> subscriptions
            -> subscription_events
            -> customer_invoice_lines
            -> revenue_schedules
        -> projects
            -> project_milestones
            -> time_entries
            -> customer_invoice_lines
            -> revenue_schedules

customer_invoices
    -> customer_invoice_lines
    -> customer_payments

suppliers
    -> purchases
        -> purchase_lines
    -> supplier_invoices
        -> supplier_invoice_lines

employees
    -> payroll
    -> headcount_events
    -> time_entries

revenue_schedules
    -> journal_headers(source_type='REVENUE_SCHEDULE', source_id)
        -> journal_lines

supplier_invoices
    -> journal_headers(source_type='SUPPLIER_INVOICE', source_id)
        -> journal_lines

payroll
    -> journal_headers(source_type='PAYROLL', source_id)
        -> journal_lines

planning facts
    -> conformed dimensions
    -> compare to aggregated journal_lines

scenarios
    -> scenario_ground_truth  [evaluator-only]
    -> investigation_questions
        -> expected_answers   [evaluator-only criteria]
```

## Constraint Decisions

### Customer Invoice Line Source Constraint

`customer_invoice_lines` must distinguish source motion:

- `source_type`
- `subscription_id` nullable
- `project_id` nullable

Minimum source types:

- `SUBSCRIPTION`
- `PROJECT`
- `OTHER`

Conceptual CHECK behavior:

- `SUBSCRIPTION`: `subscription_id` not null, `project_id` null.
- `PROJECT`: `project_id` not null, `subscription_id` null.
- `OTHER`: both may be null according to documented V1 rules.

This protects semantic integrity while allowing SaaS and Services to share billing infrastructure.

### Revenue Schedule Source Constraint

`revenue_schedules` must distinguish revenue source:

- `revenue_source_type`
- `subscription_id` nullable
- `project_id` nullable

Conceptual CHECK behavior:

- `SUBSCRIPTION`: `subscription_id` not null, `project_id` null.
- `PROJECT`: `project_id` not null, `subscription_id` null.

Revenue schedules remain the recognised-revenue source before journal posting. Do not create duplicate recognised-revenue truth in `project_milestones` or `subscriptions`.

### Planning Grain

Budgets and forecasts should support nullable dimensions where appropriate, especially:

- `business_unit_id`
- `region_id`
- `cost_centre_id`

`gl_account_id` and `period` remain required for financial planning facts.

Actual may exist at a finer grain. Actual must be aggregated to the relevant planning grain before variance comparison.

Do not generate fake dimension members merely to satisfy a NOT NULL planning constraint.

### Journal Lineage

V1 uses:

```text
journal_headers.source_type
journal_headers.source_id
```

This provides polymorphic lineage to sources such as:

- `REVENUE_SCHEDULE`
- `SUPPLIER_INVOICE`
- `PAYROLL`
- Future accounting sources.

PostgreSQL cannot enforce a normal FK from `source_id` to multiple possible source tables.

V1 source existence and integrity must therefore be validated by the synthetic-data generator/application layer.

Do not introduce `accounting_events` in V1.

`accounting_events` may be considered later as a hardening path if polymorphic lineage becomes too weak for production-style constraints.

## ERD Review

V1 review decisions:

- No orphan core operational tables: each core operational fact links to a root entity and either billing, revenue recognition, or accounting.
- No unnecessary bidirectional foreign keys except the documented nullable cost-centre manager relationship.
- SaaS subscriptions and Professional Services projects remain distinct operational models.
- Both revenue motions converge through customer billing and `revenue_schedules`.
- `journal_lines` remain the accounting actual source of truth.
- Planning facts use conformed dimensions and may exist at a coarser grain than actuals.
- Evaluation ground truth remains outside agent-visible investigation paths.
- No new tables are added solely because they may be useful someday.
