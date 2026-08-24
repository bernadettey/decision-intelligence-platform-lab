INSERT INTO operations.simulation_control (
    simulation_id,
    current_simulation_date,
    last_run_at,
    random_seed,
    simulation_speed,
    run_status,
    current_batch_id
) VALUES
    (1, '2024-02-29', NOW(), 424242, 'MONTHLY', 'READY', NULL);

INSERT INTO operations.ingestion_batches (
    batch_id,
    simulation_id,
    simulation_date,
    batch_type,
    started_at,
    completed_at,
    status,
    records_generated
) VALUES
    (1, 1, '2024-02-29', 'BOOTSTRAP', NOW(), NOW(), 'SUCCEEDED', 75);

UPDATE operations.simulation_control
SET current_batch_id = 1,
    updated_at = NOW()
WHERE simulation_id = 1;

INSERT INTO master.business_units (business_unit_id, business_unit_name) VALUES
    (1, 'SaaS'),
    (2, 'Professional Services'),
    (3, 'Shared Operations');

INSERT INTO master.regions (region_id, region_name) VALUES
    (1, 'North America'),
    (2, 'APAC'),
    (3, 'EMEA');

INSERT INTO master.departments (department_id, department_name) VALUES
    (1, 'Sales'),
    (2, 'Delivery'),
    (3, 'Finance'),
    (4, 'Product');

INSERT INTO master.currencies (currency_code, currency_name) VALUES
    ('USD', 'US Dollar'),
    ('AUD', 'Australian Dollar'),
    ('EUR', 'Euro');

INSERT INTO master.gl_accounts (
    gl_account_id,
    account_code,
    account_name,
    account_type,
    normal_balance
) VALUES
    (1, '4000', 'Recognised Revenue', 'REVENUE', 'CREDIT'),
    (2, '4100', 'Deferred Revenue', 'DEFERRED_REVENUE', 'CREDIT'),
    (3, '5000', 'Cost of Goods Sold', 'COGS', 'DEBIT'),
    (4, '6000', 'Payroll Expense', 'OPEX', 'DEBIT'),
    (5, '1000', 'Cash', 'CASH', 'DEBIT'),
    (6, '1100', 'Accounts Receivable', 'ASSET', 'DEBIT'),
    (7, '2000', 'Accounts Payable', 'LIABILITY', 'CREDIT');

INSERT INTO master.cost_centres (
    cost_centre_id,
    cost_centre_name,
    business_unit_id,
    department_id,
    manager_employee_id
) VALUES
    (1, 'SaaS Sales', 1, 1, NULL),
    (2, 'Services Delivery', 2, 2, NULL),
    (3, 'Finance Shared Services', NULL, 3, NULL);

INSERT INTO master.customers (
    customer_id,
    customer_name,
    region_id,
    business_unit_id,
    customer_segment
) VALUES
    (1, 'Acme Bank', 2, 1, 'Enterprise'),
    (2, 'Northstar Health', 1, 2, 'Mid-Market');

INSERT INTO master.products (
    product_id,
    product_name,
    product_family,
    business_unit_id
) VALUES
    (1, 'Decision Cloud Enterprise', 'Decision Intelligence Platform', 1),
    (2, 'Decision Cloud Usage Pack', 'Decision Intelligence Platform', 1);

INSERT INTO master.suppliers (
    supplier_id,
    supplier_name,
    supplier_category,
    region_id,
    currency_code
) VALUES
    (1, 'CloudCompute Co', 'Cloud Infrastructure', 1, 'USD'),
    (2, 'Contractor Collective', 'Delivery Contractors', 2, 'AUD');

INSERT INTO master.employees (
    employee_id,
    employee_name,
    role_title,
    business_unit_id,
    region_id,
    department_id,
    cost_centre_id,
    manager_employee_id,
    employment_status,
    start_date
) VALUES
    (1, 'Jordan Lee', 'Finance Manager', 3, 2, 3, 3, NULL, 'ACTIVE', '2023-01-01'),
    (2, 'Priya Shah', 'Delivery Consultant', 2, 2, 2, 2, 1, 'ACTIVE', '2023-02-01'),
    (3, 'Alex Chen', 'Account Executive', 1, 2, 1, 1, 1, 'ACTIVE', '2023-03-01');

UPDATE master.cost_centres
SET manager_employee_id = CASE cost_centre_id
    WHEN 1 THEN 3
    WHEN 2 THEN 2
    WHEN 3 THEN 1
END
WHERE cost_centre_id IN (1, 2, 3);

INSERT INTO operations.customer_contracts (
    contract_id,
    customer_id,
    contract_type,
    contract_start_date,
    contract_end_date,
    contract_value,
    currency_code,
    business_unit_id,
    region_id,
    contract_status
) VALUES
    (1, 1, 'SAAS', '2024-01-01', '2024-12-31', 120000.00, 'USD', 1, 2, 'ACTIVE'),
    (2, 2, 'PROFESSIONAL_SERVICES', '2024-01-15', '2024-06-30', 80000.00, 'USD', 2, 1, 'ACTIVE');

INSERT INTO operations.subscriptions (
    subscription_id,
    contract_id,
    customer_id,
    product_id,
    business_unit_id,
    region_id,
    start_date,
    end_date,
    billing_frequency,
    arr_amount,
    mrr_amount,
    subscription_status
) VALUES
    (1, 1, 1, 1, 1, 2, '2024-01-01', '2024-12-31', 'ANNUAL', 120000.00, 10000.00, 'ACTIVE');

INSERT INTO operations.subscription_events (
    subscription_event_id,
    subscription_id,
    customer_id,
    product_id,
    event_date,
    event_type,
    arr_delta,
    mrr_delta,
    event_reason
) VALUES
    (1, 1, 1, 1, '2024-01-01', 'NEW', 120000.00, 10000.00, 'New annual subscription');

INSERT INTO operations.projects (
    project_id,
    contract_id,
    customer_id,
    project_name,
    project_status,
    start_date,
    end_date,
    contracted_amount,
    currency_code,
    business_unit_id,
    region_id
) VALUES
    (1, 2, 2, 'Northstar Implementation', 'ACTIVE', '2024-01-15', '2024-06-30', 80000.00, 'USD', 2, 1);

INSERT INTO operations.project_milestones (
    milestone_id,
    project_id,
    milestone_name,
    planned_date,
    actual_date,
    milestone_amount,
    milestone_status
) VALUES
    (1, 1, 'Kickoff Complete', '2024-02-01', '2024-02-01', 20000.00, 'COMPLETED');

INSERT INTO operations.time_entries (
    time_entry_id,
    project_id,
    employee_id,
    entry_date,
    hours,
    billable_flag,
    hourly_cost_rate,
    hourly_bill_rate
) VALUES
    (1, 1, 2, '2024-02-01', 8.00, TRUE, 90.00, 180.00);

INSERT INTO operations.customer_invoices (
    customer_invoice_id,
    customer_id,
    contract_id,
    invoice_date,
    due_date,
    currency_code,
    invoice_status,
    invoice_total
) VALUES
    (1, 1, 1, '2024-01-01', '2024-01-31', 'USD', 'ISSUED', 120000.00),
    (2, 2, 2, '2024-02-01', '2024-02-29', 'USD', 'ISSUED', 20000.00);

INSERT INTO operations.customer_invoice_lines (
    customer_invoice_line_id,
    customer_invoice_id,
    source_type,
    subscription_id,
    project_id,
    line_amount,
    currency_code,
    description,
    gl_account_id
) VALUES
    (1, 1, 'SUBSCRIPTION', 1, NULL, 120000.00, 'USD', 'Annual SaaS subscription billing', 2),
    (2, 2, 'PROJECT', NULL, 1, 20000.00, 'USD', 'Implementation kickoff milestone billing', 1);

INSERT INTO operations.purchases (
    purchase_id,
    supplier_id,
    purchase_date,
    currency_code,
    purchase_status,
    business_unit_id,
    region_id,
    cost_centre_id
) VALUES
    (1, 1, '2024-01-15', 'USD', 'APPROVED', 1, 1, 1);

INSERT INTO operations.purchase_lines (
    purchase_line_id,
    purchase_id,
    product_id,
    item_description,
    quantity,
    unit_price,
    line_amount,
    currency_code,
    gl_account_id
) VALUES
    (1, 1, NULL, 'Cloud infrastructure usage', 100.00, 25.00, 2500.00, 'USD', 3);

INSERT INTO operations.supplier_invoices (
    supplier_invoice_id,
    supplier_id,
    purchase_id,
    invoice_date,
    due_date,
    currency_code,
    invoice_total,
    invoice_status
) VALUES
    (1, 1, 1, '2024-01-31', '2024-02-15', 'USD', 2500.00, 'APPROVED');

INSERT INTO operations.supplier_invoice_lines (
    supplier_invoice_line_id,
    supplier_invoice_id,
    purchase_line_id,
    gl_account_id,
    line_amount,
    currency_code,
    description
) VALUES
    (1, 1, 1, 3, 2500.00, 'USD', 'Cloud infrastructure cost');

INSERT INTO operations.payroll (
    payroll_id,
    employee_id,
    period,
    cost_centre_id,
    business_unit_id,
    region_id,
    salary_amount,
    bonus_amount,
    benefits_amount,
    total_payroll_cost,
    currency_code,
    gl_account_id
) VALUES
    (1, 2, '2024-02-01', 2, 2, 2, 10000.00, 0.00, 2000.00, 12000.00, 'USD', 4);

INSERT INTO operations.headcount_events (
    headcount_event_id,
    employee_id,
    event_date,
    event_type,
    cost_centre_id,
    business_unit_id,
    region_id,
    fte_change
) VALUES
    (1, 2, '2023-02-01', 'HIRE', 2, 2, 2, 1.00);

INSERT INTO operations.business_events (
    business_event_id,
    event_date,
    event_type,
    event_description,
    business_unit_id,
    region_id,
    customer_id,
    supplier_id,
    employee_id,
    project_id,
    subscription_id,
    severity
) VALUES
    (1, '2024-01-01', 'customer_contract_delay', 'Annual SaaS contract started on schedule for Acme Bank.', 1, 2, 1, NULL, NULL, NULL, 1, 'LOW');

INSERT INTO operations.fx_rates (
    fx_rate_id,
    rate_date,
    from_currency_code,
    to_currency_code,
    exchange_rate
) VALUES
    (1, '2024-01-01', 'USD', 'AUD', 1.50000000),
    (2, '2024-01-01', 'EUR', 'USD', 1.10000000);

INSERT INTO finance.revenue_schedules (
    revenue_schedule_id,
    revenue_source_type,
    subscription_id,
    project_id,
    customer_invoice_line_id,
    customer_id,
    recognition_period,
    scheduled_amount,
    recognised_amount,
    currency_code,
    gl_account_id,
    recognition_status
) VALUES
    (1, 'SUBSCRIPTION', 1, NULL, 1, 1, '2024-01-01', 10000.00, 10000.00, 'USD', 1, 'RECOGNISED'),
    (2, 'PROJECT', NULL, 1, 2, 2, '2024-02-01', 20000.00, 20000.00, 'USD', 1, 'RECOGNISED');

INSERT INTO finance.journal_headers (
    journal_header_id,
    journal_date,
    period,
    source_type,
    source_id,
    description,
    currency_code,
    posted_flag
) VALUES
    (1, '2024-01-31', '2024-01-01', 'REVENUE_SCHEDULE', 1, 'Recognise January SaaS revenue', 'USD', TRUE),
    (2, '2024-01-31', '2024-01-01', 'SUPPLIER_INVOICE', 1, 'Record cloud supplier invoice', 'USD', TRUE),
    (3, '2024-02-29', '2024-02-01', 'PAYROLL', 1, 'Record February delivery payroll', 'USD', TRUE);

INSERT INTO finance.journal_lines (
    journal_line_id,
    journal_header_id,
    gl_account_id,
    period,
    debit_amount,
    credit_amount,
    net_amount,
    currency_code,
    business_unit_id,
    region_id,
    cost_centre_id,
    customer_id,
    supplier_id,
    employee_id,
    project_id,
    subscription_id
) VALUES
    (1, 1, 2, '2024-01-01', 10000.00, 0.00, 10000.00, 'USD', 1, 2, NULL, 1, NULL, NULL, NULL, 1),
    (2, 1, 1, '2024-01-01', 0.00, 10000.00, -10000.00, 'USD', 1, 2, NULL, 1, NULL, NULL, NULL, 1),
    (3, 2, 3, '2024-01-01', 2500.00, 0.00, 2500.00, 'USD', 1, 1, 1, NULL, 1, NULL, NULL, NULL),
    (4, 2, 7, '2024-01-01', 0.00, 2500.00, -2500.00, 'USD', 1, 1, 1, NULL, 1, NULL, NULL, NULL),
    (5, 3, 4, '2024-02-01', 12000.00, 0.00, 12000.00, 'USD', 2, 2, 2, NULL, NULL, 2, 1, NULL),
    (6, 3, 7, '2024-02-01', 0.00, 12000.00, -12000.00, 'USD', 2, 2, 2, NULL, NULL, 2, 1, NULL);

INSERT INTO planning.forecast_versions (
    forecast_version_id,
    version_name,
    forecast_cutoff_date,
    status
) VALUES
    (1, 'FY2024 Forecast v1', '2024-01-31', 'ACTIVE');

INSERT INTO planning.budgets (
    budget_id,
    period,
    gl_account_id,
    business_unit_id,
    region_id,
    cost_centre_id,
    budget_amount,
    currency_code
) VALUES
    (1, '2024-01-01', 1, 1, 2, NULL, -11000.00, 'USD'),
    (2, '2024-01-01', 3, NULL, NULL, 1, 3000.00, 'USD'),
    (3, '2024-02-01', 4, NULL, NULL, 2, 11000.00, 'USD');

INSERT INTO planning.forecasts (
    forecast_id,
    forecast_version_id,
    period,
    gl_account_id,
    business_unit_id,
    region_id,
    cost_centre_id,
    forecast_amount,
    currency_code
) VALUES
    (1, 1, '2024-01-01', 1, 1, 2, NULL, -12000.00, 'USD'),
    (2, 1, '2024-01-01', 3, NULL, NULL, 1, 2600.00, 'USD'),
    (3, 1, '2024-02-01', 4, NULL, NULL, 2, 11500.00, 'USD');

INSERT INTO planning.headcount_plan (
    headcount_plan_id,
    period,
    business_unit_id,
    region_id,
    department_id,
    cost_centre_id,
    planned_fte,
    planned_payroll_cost,
    currency_code
) VALUES
    (1, '2024-02-01', 2, 2, 2, 2, 4.00, 45000.00, 'USD');

INSERT INTO evaluation.scenarios (
    scenario_id,
    scenario_type,
    scenario_name,
    period,
    severity,
    business_unit_id,
    region_id,
    customer_id,
    supplier_id
) VALUES
    (1, 'supplier_price_increase', 'Cloud supplier unit cost increase', '2024-01-01', 'MEDIUM', 1, 1, NULL, 1);

INSERT INTO evaluation.scenario_ground_truth (
    scenario_ground_truth_id,
    scenario_id,
    primary_root_cause,
    expected_driver,
    expected_financial_impact,
    expected_kpi_impact,
    expected_causal_chain
) VALUES
    (
        1,
        1,
        'Cloud supplier unit price increased',
        'unit_price',
        'COGS increased through supplier invoice lines and journal lines',
        'Gross margin and EBITDA decreased',
        'Business Event -> Operational Driver -> Supplier Invoice -> Journal Lines -> EBITDA Variance'
    );

INSERT INTO evaluation.investigation_questions (
    investigation_question_id,
    scenario_id,
    question_text,
    persona,
    expected_answerability,
    ambiguity_behavior
) VALUES
    (
        1,
        1,
        'Why did gross margin miss forecast in North America?',
        'Finance Manager',
        'SUPPORTED',
        'AUTO_RESOLVE'
    );

INSERT INTO evaluation.expected_answers (
    expected_answer_id,
    investigation_question_id,
    scenario_id,
    required_root_cause,
    required_evidence,
    required_kpi_impact,
    unsupported_claims
) VALUES
    (
        1,
        1,
        1,
        'Cloud supplier unit price increased',
        'Supplier invoice line cost and journal line COGS evidence',
        'Gross margin and EBITDA decreased',
        NULL
    );

SELECT setval('master.business_units_business_unit_id_seq', 3, TRUE);
SELECT setval('master.regions_region_id_seq', 3, TRUE);
SELECT setval('master.departments_department_id_seq', 4, TRUE);
SELECT setval('master.gl_accounts_gl_account_id_seq', 7, TRUE);
SELECT setval('master.cost_centres_cost_centre_id_seq', 3, TRUE);
SELECT setval('master.customers_customer_id_seq', 2, TRUE);
SELECT setval('master.products_product_id_seq', 2, TRUE);
SELECT setval('master.suppliers_supplier_id_seq', 2, TRUE);
SELECT setval('master.employees_employee_id_seq', 3, TRUE);
SELECT setval('operations.customer_contracts_contract_id_seq', 2, TRUE);
SELECT setval('operations.subscriptions_subscription_id_seq', 1, TRUE);
SELECT setval('operations.subscription_events_subscription_event_id_seq', 1, TRUE);
SELECT setval('operations.projects_project_id_seq', 1, TRUE);
SELECT setval('operations.project_milestones_milestone_id_seq', 1, TRUE);
SELECT setval('operations.time_entries_time_entry_id_seq', 1, TRUE);
SELECT setval('operations.customer_invoices_customer_invoice_id_seq', 2, TRUE);
SELECT setval('operations.customer_invoice_lines_customer_invoice_line_id_seq', 2, TRUE);
SELECT setval('operations.purchases_purchase_id_seq', 1, TRUE);
SELECT setval('operations.purchase_lines_purchase_line_id_seq', 1, TRUE);
SELECT setval('operations.supplier_invoices_supplier_invoice_id_seq', 1, TRUE);
SELECT setval('operations.supplier_invoice_lines_supplier_invoice_line_id_seq', 1, TRUE);
SELECT setval('operations.payroll_payroll_id_seq', 1, TRUE);
SELECT setval('operations.headcount_events_headcount_event_id_seq', 1, TRUE);
SELECT setval('operations.business_events_business_event_id_seq', 1, TRUE);
SELECT setval('operations.fx_rates_fx_rate_id_seq', 2, TRUE);
SELECT setval('finance.revenue_schedules_revenue_schedule_id_seq', 2, TRUE);
SELECT setval('finance.journal_headers_journal_header_id_seq', 3, TRUE);
SELECT setval('finance.journal_lines_journal_line_id_seq', 6, TRUE);
SELECT setval('planning.forecast_versions_forecast_version_id_seq', 1, TRUE);
SELECT setval('planning.budgets_budget_id_seq', 3, TRUE);
SELECT setval('planning.forecasts_forecast_id_seq', 3, TRUE);
SELECT setval('planning.headcount_plan_headcount_plan_id_seq', 1, TRUE);
SELECT setval('evaluation.scenarios_scenario_id_seq', 1, TRUE);
SELECT setval('evaluation.scenario_ground_truth_scenario_ground_truth_id_seq', 1, TRUE);
SELECT setval('evaluation.investigation_questions_investigation_question_id_seq', 1, TRUE);
SELECT setval('evaluation.expected_answers_expected_answer_id_seq', 1, TRUE);
SELECT setval('operations.simulation_control_simulation_id_seq', 1, TRUE);
SELECT setval('operations.ingestion_batches_batch_id_seq', 1, TRUE);
