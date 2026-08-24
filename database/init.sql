CREATE SCHEMA IF NOT EXISTS master;
CREATE SCHEMA IF NOT EXISTS operations;
CREATE SCHEMA IF NOT EXISTS finance;
CREATE SCHEMA IF NOT EXISTS planning;
CREATE SCHEMA IF NOT EXISTS evaluation;

CREATE TABLE operations.simulation_control (
    simulation_id SERIAL PRIMARY KEY,
    current_simulation_date DATE NOT NULL,
    last_run_at TIMESTAMPTZ NULL,
    random_seed INTEGER NOT NULL,
    simulation_speed VARCHAR(20) NOT NULL CHECK (
        simulation_speed IN ('DAILY', 'WEEKLY', 'MONTHLY')
    ),
    run_status VARCHAR(20) NOT NULL CHECK (
        run_status IN ('READY', 'RUNNING', 'PAUSED', 'FAILED')
    ),
    current_batch_id INTEGER NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE operations.ingestion_batches (
    batch_id SERIAL PRIMARY KEY,
    simulation_id INTEGER NOT NULL REFERENCES operations.simulation_control(simulation_id),
    simulation_date DATE NOT NULL,
    batch_type VARCHAR(20) NOT NULL CHECK (
        batch_type IN ('BOOTSTRAP', 'INCREMENTAL', 'REPLAY')
    ),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ NULL,
    status VARCHAR(20) NOT NULL CHECK (
        status IN ('STARTED', 'SUCCEEDED', 'FAILED')
    ),
    records_generated INTEGER NOT NULL DEFAULT 0 CHECK (records_generated >= 0),
    generator_version VARCHAR(80) NOT NULL DEFAULT 'manual-bootstrap',
    error_message TEXT NULL
);

ALTER TABLE operations.simulation_control
    ADD CONSTRAINT fk_simulation_control_current_batch
    FOREIGN KEY (current_batch_id)
    REFERENCES operations.ingestion_batches(batch_id);

CREATE TABLE master.business_units (
    business_unit_id SERIAL PRIMARY KEY,
    business_unit_name VARCHAR(120) NOT NULL UNIQUE,
    active_flag BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE master.regions (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(120) NOT NULL UNIQUE,
    active_flag BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE master.departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(120) NOT NULL UNIQUE,
    active_flag BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE master.currencies (
    currency_code CHAR(3) PRIMARY KEY,
    currency_name VARCHAR(120) NOT NULL,
    active_flag BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE master.gl_accounts (
    gl_account_id SERIAL PRIMARY KEY,
    account_code VARCHAR(40) NOT NULL UNIQUE,
    account_name VARCHAR(160) NOT NULL,
    account_type VARCHAR(40) NOT NULL CHECK (
        account_type IN (
            'REVENUE',
            'COGS',
            'OPEX',
            'ASSET',
            'LIABILITY',
            'EQUITY',
            'CASH',
            'DEFERRED_REVENUE'
        )
    ),
    normal_balance VARCHAR(10) NOT NULL CHECK (normal_balance IN ('DEBIT', 'CREDIT')),
    active_flag BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE master.cost_centres (
    cost_centre_id SERIAL PRIMARY KEY,
    cost_centre_name VARCHAR(120) NOT NULL UNIQUE,
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    department_id INTEGER NULL REFERENCES master.departments(department_id),
    manager_employee_id INTEGER NULL,
    active_flag BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE master.customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(160) NOT NULL UNIQUE,
    region_id INTEGER NOT NULL REFERENCES master.regions(region_id),
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    customer_segment VARCHAR(80) NOT NULL,
    active_flag BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE master.products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(160) NOT NULL UNIQUE,
    product_family VARCHAR(100) NOT NULL,
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    active_flag BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE master.suppliers (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name VARCHAR(160) NOT NULL UNIQUE,
    supplier_category VARCHAR(100) NOT NULL,
    region_id INTEGER NULL REFERENCES master.regions(region_id),
    currency_code CHAR(3) NULL REFERENCES master.currencies(currency_code),
    active_flag BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE master.employees (
    employee_id SERIAL PRIMARY KEY,
    employee_name VARCHAR(160) NOT NULL,
    role_title VARCHAR(120) NOT NULL,
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    region_id INTEGER NULL REFERENCES master.regions(region_id),
    department_id INTEGER NULL REFERENCES master.departments(department_id),
    cost_centre_id INTEGER NOT NULL REFERENCES master.cost_centres(cost_centre_id),
    manager_employee_id INTEGER NULL REFERENCES master.employees(employee_id),
    employment_status VARCHAR(40) NOT NULL CHECK (
        employment_status IN ('ACTIVE', 'TERMINATED', 'ON_LEAVE')
    ),
    start_date DATE NOT NULL,
    end_date DATE NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id),
    record_version INTEGER NOT NULL DEFAULT 1 CHECK (record_version >= 1),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (end_date IS NULL OR end_date >= start_date)
);

ALTER TABLE master.cost_centres
    ADD CONSTRAINT fk_cost_centres_manager_employee
    FOREIGN KEY (manager_employee_id)
    REFERENCES master.employees(employee_id);

CREATE TABLE operations.customer_contracts (
    contract_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES master.customers(customer_id),
    contract_type VARCHAR(40) NOT NULL CHECK (
        contract_type IN ('SAAS', 'PROFESSIONAL_SERVICES', 'MIXED')
    ),
    contract_start_date DATE NOT NULL,
    contract_end_date DATE NULL,
    contract_value NUMERIC(14, 2) NOT NULL CHECK (contract_value >= 0),
    currency_code CHAR(3) NOT NULL REFERENCES master.currencies(currency_code),
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    region_id INTEGER NULL REFERENCES master.regions(region_id),
    contract_status VARCHAR(40) NOT NULL CHECK (
        contract_status IN ('DRAFT', 'ACTIVE', 'COMPLETED', 'CANCELLED')
    ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id),
    record_version INTEGER NOT NULL DEFAULT 1 CHECK (record_version >= 1),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (contract_end_date IS NULL OR contract_end_date >= contract_start_date)
);

CREATE TABLE operations.subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES operations.customer_contracts(contract_id),
    customer_id INTEGER NOT NULL REFERENCES master.customers(customer_id),
    product_id INTEGER NOT NULL REFERENCES master.products(product_id),
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    region_id INTEGER NULL REFERENCES master.regions(region_id),
    start_date DATE NOT NULL,
    end_date DATE NULL,
    billing_frequency VARCHAR(20) NOT NULL CHECK (
        billing_frequency IN ('MONTHLY', 'QUARTERLY', 'ANNUAL')
    ),
    arr_amount NUMERIC(14, 2) NOT NULL CHECK (arr_amount >= 0),
    mrr_amount NUMERIC(14, 2) NOT NULL CHECK (mrr_amount >= 0),
    subscription_status VARCHAR(40) NOT NULL CHECK (
        subscription_status IN ('ACTIVE', 'CHURNED', 'PAUSED', 'ENDED')
    ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id),
    record_version INTEGER NOT NULL DEFAULT 1 CHECK (record_version >= 1),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE operations.subscription_events (
    subscription_event_id SERIAL PRIMARY KEY,
    subscription_id INTEGER NOT NULL REFERENCES operations.subscriptions(subscription_id),
    customer_id INTEGER NOT NULL REFERENCES master.customers(customer_id),
    product_id INTEGER NULL REFERENCES master.products(product_id),
    event_date DATE NOT NULL,
    event_type VARCHAR(40) NOT NULL CHECK (
        event_type IN ('NEW', 'RENEWAL', 'EXPANSION', 'CONTRACTION', 'CHURN')
    ),
    arr_delta NUMERIC(14, 2) NOT NULL,
    mrr_delta NUMERIC(14, 2) NOT NULL,
    event_reason TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id)
);

CREATE TABLE operations.projects (
    project_id SERIAL PRIMARY KEY,
    contract_id INTEGER NOT NULL REFERENCES operations.customer_contracts(contract_id),
    customer_id INTEGER NOT NULL REFERENCES master.customers(customer_id),
    project_name VARCHAR(160) NOT NULL,
    project_status VARCHAR(40) NOT NULL CHECK (
        project_status IN ('PLANNED', 'ACTIVE', 'COMPLETED', 'CANCELLED')
    ),
    start_date DATE NOT NULL,
    end_date DATE NULL,
    contracted_amount NUMERIC(14, 2) NOT NULL CHECK (contracted_amount >= 0),
    currency_code CHAR(3) NOT NULL REFERENCES master.currencies(currency_code),
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    region_id INTEGER NULL REFERENCES master.regions(region_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id),
    record_version INTEGER NOT NULL DEFAULT 1 CHECK (record_version >= 1),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE operations.project_milestones (
    milestone_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES operations.projects(project_id),
    milestone_name VARCHAR(160) NOT NULL,
    planned_date DATE NOT NULL,
    actual_date DATE NULL,
    milestone_amount NUMERIC(14, 2) NOT NULL CHECK (milestone_amount >= 0),
    milestone_status VARCHAR(40) NOT NULL CHECK (
        milestone_status IN ('PLANNED', 'COMPLETED', 'DELAYED', 'CANCELLED')
    ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id),
    record_version INTEGER NOT NULL DEFAULT 1 CHECK (record_version >= 1),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE operations.time_entries (
    time_entry_id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES operations.projects(project_id),
    employee_id INTEGER NOT NULL REFERENCES master.employees(employee_id),
    entry_date DATE NOT NULL,
    hours NUMERIC(8, 2) NOT NULL CHECK (hours >= 0),
    billable_flag BOOLEAN NOT NULL DEFAULT FALSE,
    hourly_cost_rate NUMERIC(10, 2) NOT NULL CHECK (hourly_cost_rate >= 0),
    hourly_bill_rate NUMERIC(10, 2) NULL CHECK (hourly_bill_rate IS NULL OR hourly_bill_rate >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id)
);

CREATE TABLE operations.customer_invoices (
    customer_invoice_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES master.customers(customer_id),
    contract_id INTEGER NULL REFERENCES operations.customer_contracts(contract_id),
    invoice_date DATE NOT NULL,
    due_date DATE NULL,
    currency_code CHAR(3) NOT NULL REFERENCES master.currencies(currency_code),
    invoice_status VARCHAR(40) NOT NULL CHECK (
        invoice_status IN ('DRAFT', 'ISSUED', 'PAID', 'VOID')
    ),
    invoice_total NUMERIC(14, 2) NOT NULL CHECK (invoice_total >= 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id),
    record_version INTEGER NOT NULL DEFAULT 1 CHECK (record_version >= 1),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE operations.customer_invoice_lines (
    customer_invoice_line_id SERIAL PRIMARY KEY,
    customer_invoice_id INTEGER NOT NULL REFERENCES operations.customer_invoices(customer_invoice_id),
    source_type VARCHAR(20) NOT NULL CHECK (source_type IN ('SUBSCRIPTION', 'PROJECT', 'OTHER')),
    subscription_id INTEGER NULL REFERENCES operations.subscriptions(subscription_id),
    project_id INTEGER NULL REFERENCES operations.projects(project_id),
    line_amount NUMERIC(14, 2) NOT NULL CHECK (line_amount >= 0),
    currency_code CHAR(3) NOT NULL REFERENCES master.currencies(currency_code),
    description TEXT NULL,
    gl_account_id INTEGER NULL REFERENCES master.gl_accounts(gl_account_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id),
    CONSTRAINT chk_customer_invoice_lines_source
        CHECK (
            (source_type = 'SUBSCRIPTION' AND subscription_id IS NOT NULL AND project_id IS NULL)
            OR (source_type = 'PROJECT' AND project_id IS NOT NULL AND subscription_id IS NULL)
            OR (source_type = 'OTHER' AND subscription_id IS NULL AND project_id IS NULL)
        )
);

CREATE TABLE operations.purchases (
    purchase_id SERIAL PRIMARY KEY,
    supplier_id INTEGER NOT NULL REFERENCES master.suppliers(supplier_id),
    purchase_date DATE NOT NULL,
    currency_code CHAR(3) NOT NULL REFERENCES master.currencies(currency_code),
    purchase_status VARCHAR(40) NOT NULL CHECK (
        purchase_status IN ('DRAFT', 'APPROVED', 'RECEIVED', 'CANCELLED')
    ),
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    region_id INTEGER NULL REFERENCES master.regions(region_id),
    cost_centre_id INTEGER NULL REFERENCES master.cost_centres(cost_centre_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id),
    record_version INTEGER NOT NULL DEFAULT 1 CHECK (record_version >= 1),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE operations.purchase_lines (
    purchase_line_id SERIAL PRIMARY KEY,
    purchase_id INTEGER NOT NULL REFERENCES operations.purchases(purchase_id),
    product_id INTEGER NULL REFERENCES master.products(product_id),
    item_description TEXT NOT NULL,
    quantity NUMERIC(12, 2) NOT NULL CHECK (quantity >= 0),
    unit_price NUMERIC(14, 2) NOT NULL CHECK (unit_price >= 0),
    line_amount NUMERIC(14, 2) NOT NULL CHECK (line_amount >= 0),
    currency_code CHAR(3) NOT NULL REFERENCES master.currencies(currency_code),
    gl_account_id INTEGER NULL REFERENCES master.gl_accounts(gl_account_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id)
);

CREATE TABLE operations.supplier_invoices (
    supplier_invoice_id SERIAL PRIMARY KEY,
    supplier_id INTEGER NOT NULL REFERENCES master.suppliers(supplier_id),
    purchase_id INTEGER NULL REFERENCES operations.purchases(purchase_id),
    invoice_date DATE NOT NULL,
    due_date DATE NULL,
    currency_code CHAR(3) NOT NULL REFERENCES master.currencies(currency_code),
    invoice_total NUMERIC(14, 2) NOT NULL CHECK (invoice_total >= 0),
    invoice_status VARCHAR(40) NOT NULL CHECK (
        invoice_status IN ('DRAFT', 'RECEIVED', 'APPROVED', 'PAID', 'VOID')
    ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id),
    record_version INTEGER NOT NULL DEFAULT 1 CHECK (record_version >= 1),
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE operations.supplier_invoice_lines (
    supplier_invoice_line_id SERIAL PRIMARY KEY,
    supplier_invoice_id INTEGER NOT NULL REFERENCES operations.supplier_invoices(supplier_invoice_id),
    purchase_line_id INTEGER NULL REFERENCES operations.purchase_lines(purchase_line_id),
    gl_account_id INTEGER NOT NULL REFERENCES master.gl_accounts(gl_account_id),
    line_amount NUMERIC(14, 2) NOT NULL CHECK (line_amount >= 0),
    currency_code CHAR(3) NOT NULL REFERENCES master.currencies(currency_code),
    description TEXT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id)
);

CREATE TABLE operations.payroll (
    payroll_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES master.employees(employee_id),
    period DATE NOT NULL,
    cost_centre_id INTEGER NOT NULL REFERENCES master.cost_centres(cost_centre_id),
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    region_id INTEGER NULL REFERENCES master.regions(region_id),
    salary_amount NUMERIC(14, 2) NOT NULL CHECK (salary_amount >= 0),
    bonus_amount NUMERIC(14, 2) NOT NULL DEFAULT 0 CHECK (bonus_amount >= 0),
    benefits_amount NUMERIC(14, 2) NOT NULL DEFAULT 0 CHECK (benefits_amount >= 0),
    total_payroll_cost NUMERIC(14, 2) NOT NULL CHECK (total_payroll_cost >= 0),
    currency_code CHAR(3) NOT NULL REFERENCES master.currencies(currency_code),
    gl_account_id INTEGER NOT NULL REFERENCES master.gl_accounts(gl_account_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id)
);

CREATE TABLE operations.headcount_events (
    headcount_event_id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES master.employees(employee_id),
    event_date DATE NOT NULL,
    event_type VARCHAR(40) NOT NULL CHECK (
        event_type IN ('HIRE', 'TERMINATION', 'TRANSFER', 'SALARY_CHANGE')
    ),
    cost_centre_id INTEGER NULL REFERENCES master.cost_centres(cost_centre_id),
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    region_id INTEGER NULL REFERENCES master.regions(region_id),
    fte_change NUMERIC(6, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id)
);

CREATE TABLE operations.business_events (
    business_event_id SERIAL PRIMARY KEY,
    event_date DATE NOT NULL,
    event_type VARCHAR(80) NOT NULL,
    event_description TEXT NOT NULL,
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    region_id INTEGER NULL REFERENCES master.regions(region_id),
    customer_id INTEGER NULL REFERENCES master.customers(customer_id),
    supplier_id INTEGER NULL REFERENCES master.suppliers(supplier_id),
    employee_id INTEGER NULL REFERENCES master.employees(employee_id),
    project_id INTEGER NULL REFERENCES operations.projects(project_id),
    subscription_id INTEGER NULL REFERENCES operations.subscriptions(subscription_id),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id)
);

CREATE TABLE operations.fx_rates (
    fx_rate_id SERIAL PRIMARY KEY,
    rate_date DATE NOT NULL,
    from_currency_code CHAR(3) NOT NULL REFERENCES master.currencies(currency_code),
    to_currency_code CHAR(3) NOT NULL REFERENCES master.currencies(currency_code),
    exchange_rate NUMERIC(18, 8) NOT NULL CHECK (exchange_rate > 0),
    UNIQUE (rate_date, from_currency_code, to_currency_code)
);

CREATE TABLE finance.revenue_schedules (
    revenue_schedule_id SERIAL PRIMARY KEY,
    revenue_source_type VARCHAR(20) NOT NULL CHECK (revenue_source_type IN ('SUBSCRIPTION', 'PROJECT')),
    subscription_id INTEGER NULL REFERENCES operations.subscriptions(subscription_id),
    project_id INTEGER NULL REFERENCES operations.projects(project_id),
    customer_invoice_line_id INTEGER NULL REFERENCES operations.customer_invoice_lines(customer_invoice_line_id),
    customer_id INTEGER NOT NULL REFERENCES master.customers(customer_id),
    recognition_period DATE NOT NULL,
    scheduled_amount NUMERIC(14, 2) NOT NULL CHECK (scheduled_amount >= 0),
    recognised_amount NUMERIC(14, 2) NOT NULL CHECK (recognised_amount >= 0),
    currency_code CHAR(3) NOT NULL REFERENCES master.currencies(currency_code),
    gl_account_id INTEGER NOT NULL REFERENCES master.gl_accounts(gl_account_id),
    recognition_status VARCHAR(40) NOT NULL CHECK (
        recognition_status IN ('SCHEDULED', 'RECOGNISED', 'DEFERRED', 'REVERSED')
    ),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id),
    CONSTRAINT chk_revenue_schedules_source
        CHECK (
            (revenue_source_type = 'SUBSCRIPTION' AND subscription_id IS NOT NULL AND project_id IS NULL)
            OR (revenue_source_type = 'PROJECT' AND project_id IS NOT NULL AND subscription_id IS NULL)
        )
);

CREATE TABLE finance.journal_headers (
    journal_header_id SERIAL PRIMARY KEY,
    journal_date DATE NOT NULL,
    period DATE NOT NULL,
    source_type VARCHAR(40) NOT NULL CHECK (
        source_type IN ('REVENUE_SCHEDULE', 'SUPPLIER_INVOICE', 'PAYROLL')
    ),
    source_id INTEGER NOT NULL,
    description TEXT NULL,
    currency_code CHAR(3) NULL REFERENCES master.currencies(currency_code),
    posted_flag BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id)
);

CREATE TABLE finance.journal_lines (
    journal_line_id SERIAL PRIMARY KEY,
    journal_header_id INTEGER NOT NULL REFERENCES finance.journal_headers(journal_header_id),
    gl_account_id INTEGER NOT NULL REFERENCES master.gl_accounts(gl_account_id),
    period DATE NOT NULL,
    debit_amount NUMERIC(14, 2) NOT NULL DEFAULT 0 CHECK (debit_amount >= 0),
    credit_amount NUMERIC(14, 2) NOT NULL DEFAULT 0 CHECK (credit_amount >= 0),
    net_amount NUMERIC(14, 2) NOT NULL,
    currency_code CHAR(3) NOT NULL REFERENCES master.currencies(currency_code),
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    region_id INTEGER NULL REFERENCES master.regions(region_id),
    cost_centre_id INTEGER NULL REFERENCES master.cost_centres(cost_centre_id),
    customer_id INTEGER NULL REFERENCES master.customers(customer_id),
    supplier_id INTEGER NULL REFERENCES master.suppliers(supplier_id),
    employee_id INTEGER NULL REFERENCES master.employees(employee_id),
    project_id INTEGER NULL REFERENCES operations.projects(project_id),
    subscription_id INTEGER NULL REFERENCES operations.subscriptions(subscription_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_system VARCHAR(80) NOT NULL DEFAULT 'synthetic_generator',
    ingestion_batch_id INTEGER NULL REFERENCES operations.ingestion_batches(batch_id),
    CHECK (debit_amount > 0 OR credit_amount > 0),
    CHECK (NOT (debit_amount > 0 AND credit_amount > 0))
);

CREATE TABLE planning.forecast_versions (
    forecast_version_id SERIAL PRIMARY KEY,
    version_name VARCHAR(120) NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    forecast_cutoff_date DATE NOT NULL,
    status VARCHAR(40) NOT NULL CHECK (status IN ('DRAFT', 'ACTIVE', 'ARCHIVED'))
);

CREATE TABLE planning.budgets (
    budget_id SERIAL PRIMARY KEY,
    period DATE NOT NULL,
    gl_account_id INTEGER NOT NULL REFERENCES master.gl_accounts(gl_account_id),
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    region_id INTEGER NULL REFERENCES master.regions(region_id),
    cost_centre_id INTEGER NULL REFERENCES master.cost_centres(cost_centre_id),
    budget_amount NUMERIC(14, 2) NOT NULL,
    currency_code CHAR(3) NULL REFERENCES master.currencies(currency_code)
);

CREATE TABLE planning.forecasts (
    forecast_id SERIAL PRIMARY KEY,
    forecast_version_id INTEGER NOT NULL REFERENCES planning.forecast_versions(forecast_version_id),
    period DATE NOT NULL,
    gl_account_id INTEGER NOT NULL REFERENCES master.gl_accounts(gl_account_id),
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    region_id INTEGER NULL REFERENCES master.regions(region_id),
    cost_centre_id INTEGER NULL REFERENCES master.cost_centres(cost_centre_id),
    forecast_amount NUMERIC(14, 2) NOT NULL,
    currency_code CHAR(3) NULL REFERENCES master.currencies(currency_code)
);

CREATE TABLE planning.headcount_plan (
    headcount_plan_id SERIAL PRIMARY KEY,
    period DATE NOT NULL,
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    region_id INTEGER NULL REFERENCES master.regions(region_id),
    department_id INTEGER NULL REFERENCES master.departments(department_id),
    cost_centre_id INTEGER NULL REFERENCES master.cost_centres(cost_centre_id),
    planned_fte NUMERIC(8, 2) NOT NULL CHECK (planned_fte >= 0),
    planned_payroll_cost NUMERIC(14, 2) NOT NULL CHECK (planned_payroll_cost >= 0),
    currency_code CHAR(3) NULL REFERENCES master.currencies(currency_code)
);

CREATE TABLE evaluation.scenarios (
    scenario_id SERIAL PRIMARY KEY,
    scenario_type VARCHAR(100) NOT NULL,
    scenario_name VARCHAR(160) NOT NULL,
    period DATE NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH')),
    business_unit_id INTEGER NULL REFERENCES master.business_units(business_unit_id),
    region_id INTEGER NULL REFERENCES master.regions(region_id),
    customer_id INTEGER NULL REFERENCES master.customers(customer_id),
    supplier_id INTEGER NULL REFERENCES master.suppliers(supplier_id),
    active_flag BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE evaluation.scenario_ground_truth (
    scenario_ground_truth_id SERIAL PRIMARY KEY,
    scenario_id INTEGER NOT NULL REFERENCES evaluation.scenarios(scenario_id),
    primary_root_cause TEXT NOT NULL,
    expected_driver TEXT NOT NULL,
    expected_financial_impact TEXT NOT NULL,
    expected_kpi_impact TEXT NOT NULL,
    expected_causal_chain TEXT NOT NULL
);

CREATE TABLE evaluation.investigation_questions (
    investigation_question_id SERIAL PRIMARY KEY,
    scenario_id INTEGER NOT NULL REFERENCES evaluation.scenarios(scenario_id),
    question_text TEXT NOT NULL,
    persona VARCHAR(120) NULL,
    expected_answerability VARCHAR(40) NOT NULL CHECK (
        expected_answerability IN ('SUPPORTED', 'PARTIALLY_SUPPORTED', 'UNSUPPORTED')
    ),
    ambiguity_behavior VARCHAR(40) NOT NULL CHECK (
        ambiguity_behavior IN ('AUTO_RESOLVE', 'ASK_CLARIFICATION', 'MULTI_METRIC_SUMMARY')
    )
);

CREATE TABLE evaluation.expected_answers (
    expected_answer_id SERIAL PRIMARY KEY,
    investigation_question_id INTEGER NOT NULL REFERENCES evaluation.investigation_questions(investigation_question_id),
    scenario_id INTEGER NOT NULL REFERENCES evaluation.scenarios(scenario_id),
    required_root_cause TEXT NOT NULL,
    required_evidence TEXT NOT NULL,
    required_kpi_impact TEXT NOT NULL,
    unsupported_claims TEXT NULL
);

CREATE INDEX idx_operations_subscriptions_customer ON operations.subscriptions(customer_id);
CREATE INDEX idx_operations_subscription_events_subscription ON operations.subscription_events(subscription_id);
CREATE INDEX idx_operations_projects_customer ON operations.projects(customer_id);
CREATE INDEX idx_operations_customer_invoice_lines_source ON operations.customer_invoice_lines(source_type);
CREATE INDEX idx_operations_supplier_invoices_supplier ON operations.supplier_invoices(supplier_id);
CREATE INDEX idx_operations_ingestion_batches_simulation ON operations.ingestion_batches(simulation_id, simulation_date);
CREATE INDEX idx_finance_revenue_schedules_period ON finance.revenue_schedules(recognition_period);
CREATE INDEX idx_finance_journal_headers_source ON finance.journal_headers(source_type, source_id);
CREATE INDEX idx_finance_journal_lines_period ON finance.journal_lines(period);
CREATE INDEX idx_finance_journal_lines_batch ON finance.journal_lines(ingestion_batch_id);
CREATE INDEX idx_planning_budgets_period_account ON planning.budgets(period, gl_account_id);
CREATE INDEX idx_planning_forecasts_period_account ON planning.forecasts(period, gl_account_id);
