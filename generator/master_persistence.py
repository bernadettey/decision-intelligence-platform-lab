from sqlalchemy import text
from sqlalchemy.orm import Session

from generator.context import RunContext
from generator.master_data import MasterDataPopulation


class MasterDataAlreadyExistsError(RuntimeError):
    """Raised when a deterministic bootstrap population already exists."""


class MasterDataRepository:
    """Persists deterministic master data through the active simulation transaction."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def bootstrap(self, context: RunContext, population: MasterDataPopulation) -> int:
        if context.batch_id is None:
            raise ValueError("master bootstrap requires a started ingestion batch")

        self._assert_population_absent(population)

        self._insert_business_units(population.business_units)
        self._insert_regions(population.regions)
        self._insert_departments(population.departments)
        self._insert_currencies(population.currencies)
        self._insert_gl_accounts(population.gl_accounts)
        self._insert_cost_centres(population.cost_centres)
        self._insert_products(population.products)
        self._insert_customers(population.customers)
        self._insert_suppliers(population.suppliers)
        self._insert_employees(population.employees)
        self._assign_cost_centre_managers(population.manager_assignments)

        return population.total_rows

    def _assert_population_absent(self, population: MasterDataPopulation) -> None:
        checks = [
            ("master.business_units", "business_unit_id", [row["business_unit_id"] for row in population.business_units]),
            ("master.business_units", "business_unit_name", [row["business_unit_name"] for row in population.business_units]),
            ("master.regions", "region_id", [row["region_id"] for row in population.regions]),
            ("master.regions", "region_name", [row["region_name"] for row in population.regions]),
            ("master.departments", "department_id", [row["department_id"] for row in population.departments]),
            ("master.departments", "department_name", [row["department_name"] for row in population.departments]),
            ("master.cost_centres", "cost_centre_id", [row["cost_centre_id"] for row in population.cost_centres]),
            ("master.cost_centres", "cost_centre_name", [row["cost_centre_name"] for row in population.cost_centres]),
            ("master.gl_accounts", "gl_account_id", [row["gl_account_id"] for row in population.gl_accounts]),
            ("master.gl_accounts", "account_code", [row["account_code"] for row in population.gl_accounts]),
            ("master.products", "product_id", [row["product_id"] for row in population.products]),
            ("master.products", "product_name", [row["product_name"] for row in population.products]),
            ("master.customers", "customer_id", [row["customer_id"] for row in population.customers]),
            ("master.customers", "customer_name", [row["customer_name"] for row in population.customers]),
            ("master.suppliers", "supplier_id", [row["supplier_id"] for row in population.suppliers]),
            ("master.suppliers", "supplier_name", [row["supplier_name"] for row in population.suppliers]),
            ("master.employees", "employee_id", [row["employee_id"] for row in population.employees]),
        ]
        for table_name, column_name, values in checks:
            if not values:
                continue
            existing_count = self.session.execute(
                text(
                    f"""
                    SELECT count(*)
                    FROM {table_name}
                    WHERE {column_name} = ANY(:values)
                    """
                ),
                {"values": values},
            ).scalar_one()
            if existing_count:
                raise MasterDataAlreadyExistsError(
                    f"{table_name} already contains {existing_count} bootstrap key(s)"
                )

    def _insert_business_units(self, rows: list[dict[str, object]]) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO master.business_units (
                    business_unit_id, business_unit_name, active_flag
                )
                VALUES (:business_unit_id, :business_unit_name, :active_flag)
                """
            ),
            rows,
        )

    def _insert_regions(self, rows: list[dict[str, object]]) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO master.regions (region_id, region_name, active_flag)
                VALUES (:region_id, :region_name, :active_flag)
                """
            ),
            rows,
        )

    def _insert_departments(self, rows: list[dict[str, object]]) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO master.departments (department_id, department_name, active_flag)
                VALUES (:department_id, :department_name, :active_flag)
                """
            ),
            rows,
        )

    def _insert_currencies(self, rows: list[dict[str, object]]) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO master.currencies (currency_code, currency_name, active_flag)
                VALUES (:currency_code, :currency_name, :active_flag)
                ON CONFLICT (currency_code) DO NOTHING
                """
            ),
            rows,
        )

    def _insert_gl_accounts(self, rows: list[dict[str, object]]) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO master.gl_accounts (
                    gl_account_id, account_code, account_name, account_type,
                    normal_balance, active_flag
                )
                VALUES (
                    :gl_account_id, :account_code, :account_name, :account_type,
                    :normal_balance, :active_flag
                )
                """
            ),
            rows,
        )

    def _insert_cost_centres(self, rows: list[dict[str, object]]) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO master.cost_centres (
                    cost_centre_id, cost_centre_name, business_unit_id,
                    department_id, manager_employee_id, active_flag
                )
                VALUES (
                    :cost_centre_id, :cost_centre_name, :business_unit_id,
                    :department_id, :manager_employee_id, :active_flag
                )
                """
            ),
            rows,
        )

    def _insert_products(self, rows: list[dict[str, object]]) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO master.products (
                    product_id, product_name, product_family, business_unit_id, active_flag
                )
                VALUES (
                    :product_id, :product_name, :product_family, :business_unit_id, :active_flag
                )
                """
            ),
            rows,
        )

    def _insert_customers(self, rows: list[dict[str, object]]) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO master.customers (
                    customer_id, customer_name, region_id, business_unit_id,
                    customer_segment, active_flag
                )
                VALUES (
                    :customer_id, :customer_name, :region_id, :business_unit_id,
                    :customer_segment, :active_flag
                )
                """
            ),
            rows,
        )

    def _insert_suppliers(self, rows: list[dict[str, object]]) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO master.suppliers (
                    supplier_id, supplier_name, supplier_category, region_id,
                    currency_code, active_flag
                )
                VALUES (
                    :supplier_id, :supplier_name, :supplier_category, :region_id,
                    :currency_code, :active_flag
                )
                """
            ),
            rows,
        )

    def _insert_employees(self, rows: list[dict[str, object]]) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO master.employees (
                    employee_id, employee_name, role_title, business_unit_id,
                    region_id, department_id, cost_centre_id, manager_employee_id,
                    employment_status, start_date, end_date, source_system,
                    ingestion_batch_id, record_version, is_deleted
                )
                VALUES (
                    :employee_id, :employee_name, :role_title, :business_unit_id,
                    :region_id, :department_id, :cost_centre_id, :manager_employee_id,
                    :employment_status, :start_date, :end_date, :source_system,
                    :ingestion_batch_id, :record_version, :is_deleted
                )
                """
            ),
            rows,
        )

    def _assign_cost_centre_managers(self, rows: list[dict[str, int]]) -> None:
        if not rows:
            return
        self.session.execute(
            text(
                """
                UPDATE master.cost_centres
                SET manager_employee_id = :manager_employee_id
                WHERE cost_centre_id = :cost_centre_id
                """
            ),
            rows,
        )
