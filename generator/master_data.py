from dataclasses import dataclass
from datetime import date
from random import Random

from generator.context import RunContext
from generator.ids import deterministic_int_id

SOURCE_SYSTEM = "synthetic_master_bootstrap"


@dataclass(frozen=True)
class MasterDataConfig:
    departments: int = 10
    cost_centres: int = 15
    customers: int = 100
    suppliers: int = 30
    employees: int = 100


@dataclass(frozen=True)
class MasterDataPopulation:
    business_units: list[dict[str, object]]
    regions: list[dict[str, object]]
    departments: list[dict[str, object]]
    cost_centres: list[dict[str, object]]
    currencies: list[dict[str, object]]
    gl_accounts: list[dict[str, object]]
    products: list[dict[str, object]]
    customers: list[dict[str, object]]
    suppliers: list[dict[str, object]]
    employees: list[dict[str, object]]
    manager_assignments: list[dict[str, int]]

    @property
    def row_counts(self) -> dict[str, int]:
        return {
            "business_units": len(self.business_units),
            "regions": len(self.regions),
            "departments": len(self.departments),
            "cost_centres": len(self.cost_centres),
            "currencies": len(self.currencies),
            "gl_accounts": len(self.gl_accounts),
            "products": len(self.products),
            "customers": len(self.customers),
            "suppliers": len(self.suppliers),
            "employees": len(self.employees),
        }

    @property
    def total_rows(self) -> int:
        return sum(self.row_counts.values())


class MasterDataGenerator:
    def __init__(self, config: MasterDataConfig | None = None) -> None:
        self.config = config or MasterDataConfig()

    def generate(self, context: RunContext) -> MasterDataPopulation:
        rng = Random(f"{context.random_seed}:{context.generator_version}:master-bootstrap")

        business_units = self._business_units(context)
        regions = self._regions(context)
        departments = self._departments(context)
        currencies = self._currencies()
        gl_accounts = self._gl_accounts(context)
        products = self._products(context, business_units)
        cost_centres = self._cost_centres(context, business_units, departments)
        customers = self._customers(context, rng, business_units, regions)
        suppliers = self._suppliers(context, rng, regions)
        employees = self._employees(context, rng, business_units, regions, departments, cost_centres)
        manager_assignments = self._manager_assignments(cost_centres, employees)

        return MasterDataPopulation(
            business_units=business_units,
            regions=regions,
            departments=departments,
            cost_centres=cost_centres,
            currencies=currencies,
            gl_accounts=gl_accounts,
            products=products,
            customers=customers,
            suppliers=suppliers,
            employees=employees,
            manager_assignments=manager_assignments,
        )

    def _id(self, context: RunContext, table: str, key: str) -> int:
        return deterministic_int_id(
            "master",
            context.random_seed,
            context.generator_version,
            table,
            key,
        )

    def _business_units(self, context: RunContext) -> list[dict[str, object]]:
        names = ["Atlas SaaS", "Atlas Professional Services", "Atlas Corporate / Shared"]
        return [
            {
                "business_unit_id": self._id(context, "business_units", name),
                "business_unit_name": name,
                "active_flag": True,
            }
            for name in names
        ]

    def _regions(self, context: RunContext) -> list[dict[str, object]]:
        names = ["Atlas North America", "Atlas APAC", "Atlas EMEA"]
        return [
            {"region_id": self._id(context, "regions", name), "region_name": name, "active_flag": True}
            for name in names
        ]

    def _departments(self, context: RunContext) -> list[dict[str, object]]:
        names = [
            "Atlas Sales",
            "Atlas Marketing",
            "Atlas Customer Success",
            "Atlas Product",
            "Atlas Engineering",
            "Atlas Professional Services Delivery",
            "Atlas Finance",
            "Atlas People",
            "Atlas Operations",
            "Atlas Executive",
        ][: self.config.departments]
        return [
            {
                "department_id": self._id(context, "departments", name),
                "department_name": name,
                "active_flag": True,
            }
            for name in names
        ]

    def _currencies(self) -> list[dict[str, object]]:
        return [
            {"currency_code": "USD", "currency_name": "US Dollar", "active_flag": True},
            {"currency_code": "AUD", "currency_name": "Australian Dollar", "active_flag": True},
            {"currency_code": "EUR", "currency_name": "Euro", "active_flag": True},
            {"currency_code": "GBP", "currency_name": "British Pound", "active_flag": True},
            {"currency_code": "JPY", "currency_name": "Japanese Yen", "active_flag": True},
        ]

    def _gl_accounts(self, context: RunContext) -> list[dict[str, object]]:
        definitions = [
            ("9000", "Atlas Cash", "CASH", "DEBIT"),
            ("9010", "Atlas Accounts Receivable", "ASSET", "DEBIT"),
            ("9020", "Atlas Prepaid Expenses", "ASSET", "DEBIT"),
            ("9030", "Atlas Fixed Assets", "ASSET", "DEBIT"),
            ("9100", "Atlas Accounts Payable", "LIABILITY", "CREDIT"),
            ("9110", "Atlas Deferred Revenue", "DEFERRED_REVENUE", "CREDIT"),
            ("9120", "Atlas Accrued Payroll", "LIABILITY", "CREDIT"),
            ("9200", "Atlas Equity", "EQUITY", "CREDIT"),
            ("9300", "Atlas SaaS Subscription Revenue", "REVENUE", "CREDIT"),
            ("9310", "Atlas SaaS Add-on Revenue", "REVENUE", "CREDIT"),
            ("9320", "Atlas Professional Services Revenue", "REVENUE", "CREDIT"),
            ("9400", "Atlas Cloud Hosting COGS", "COGS", "DEBIT"),
            ("9410", "Atlas Support COGS", "COGS", "DEBIT"),
            ("9420", "Atlas Contractor Delivery COGS", "COGS", "DEBIT"),
            ("9500", "Atlas Sales Payroll", "OPEX", "DEBIT"),
            ("9510", "Atlas Marketing Expense", "OPEX", "DEBIT"),
            ("9520", "Atlas Engineering Payroll", "OPEX", "DEBIT"),
            ("9530", "Atlas Product Payroll", "OPEX", "DEBIT"),
            ("9540", "Atlas Customer Success Payroll", "OPEX", "DEBIT"),
            ("9550", "Atlas G&A Payroll", "OPEX", "DEBIT"),
            ("9560", "Atlas Software Tools", "OPEX", "DEBIT"),
            ("9570", "Atlas Facilities", "OPEX", "DEBIT"),
            ("9580", "Atlas Professional Fees", "OPEX", "DEBIT"),
            ("9590", "Atlas Travel", "OPEX", "DEBIT"),
        ]
        return [
            {
                "gl_account_id": self._id(context, "gl_accounts", code),
                "account_code": code,
                "account_name": name,
                "account_type": account_type,
                "normal_balance": normal_balance,
                "active_flag": True,
            }
            for code, name, account_type, normal_balance in definitions
        ]

    def _products(
        self,
        context: RunContext,
        business_units: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        bu = {row["business_unit_name"]: row["business_unit_id"] for row in business_units}
        definitions = [
            ("Atlas Decision Cloud Enterprise", "SAAS_SUBSCRIPTION", "Atlas SaaS"),
            ("Atlas Decision Cloud Growth", "SAAS_SUBSCRIPTION", "Atlas SaaS"),
            ("Atlas Decision Cloud Starter", "SAAS_SUBSCRIPTION", "Atlas SaaS"),
            ("Atlas Advanced Analytics Add-on", "SAAS_ADDON", "Atlas SaaS"),
            ("Atlas Premium Support Add-on", "SAAS_ADDON", "Atlas SaaS"),
            ("Atlas Implementation Package", "PROFESSIONAL_SERVICE", "Atlas Professional Services"),
            ("Atlas Data Migration Package", "PROFESSIONAL_SERVICE", "Atlas Professional Services"),
            ("Atlas Strategic Advisory Sprint", "PROFESSIONAL_SERVICE", "Atlas Professional Services"),
        ]
        return [
            {
                "product_id": self._id(context, "products", name),
                "product_name": name,
                "product_family": family,
                "business_unit_id": bu[bu_name],
                "active_flag": True,
            }
            for name, family, bu_name in definitions
        ]

    def _cost_centres(
        self,
        context: RunContext,
        business_units: list[dict[str, object]],
        departments: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        bu = {row["business_unit_name"]: row["business_unit_id"] for row in business_units}
        dept = {row["department_name"]: row["department_id"] for row in departments}
        definitions = [
            ("Atlas SaaS Sales NA", "Atlas SaaS", "Atlas Sales"),
            ("Atlas SaaS Sales APAC", "Atlas SaaS", "Atlas Sales"),
            ("Atlas SaaS Sales EMEA", "Atlas SaaS", "Atlas Sales"),
            ("Atlas SaaS Marketing", "Atlas SaaS", "Atlas Marketing"),
            ("Atlas Customer Success", "Atlas SaaS", "Atlas Customer Success"),
            ("Atlas Product Management", "Atlas SaaS", "Atlas Product"),
            ("Atlas Platform Engineering", "Atlas SaaS", "Atlas Engineering"),
            ("Atlas Services Delivery NA", "Atlas Professional Services", "Atlas Professional Services Delivery"),
            ("Atlas Services Delivery APAC", "Atlas Professional Services", "Atlas Professional Services Delivery"),
            ("Atlas Services Delivery EMEA", "Atlas Professional Services", "Atlas Professional Services Delivery"),
            ("Atlas Finance Shared Services", None, "Atlas Finance"),
            ("Atlas People Operations", None, "Atlas People"),
            ("Atlas Corporate Operations", None, "Atlas Operations"),
            ("Atlas Executive Office", None, "Atlas Executive"),
            ("Atlas Shared Technology", None, "Atlas Engineering"),
        ][: self.config.cost_centres]
        return [
            {
                "cost_centre_id": self._id(context, "cost_centres", name),
                "cost_centre_name": name,
                "business_unit_id": bu[bu_name] if bu_name else None,
                "department_id": dept[department_name],
                "manager_employee_id": None,
                "active_flag": True,
            }
            for name, bu_name, department_name in definitions
        ]

    def _customers(
        self,
        context: RunContext,
        rng: Random,
        business_units: list[dict[str, object]],
        regions: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        bu_id = next(row["business_unit_id"] for row in business_units if row["business_unit_name"] == "Atlas SaaS")
        segments = ["Enterprise", "Enterprise", "Mid-Market", "Mid-Market", "Strategic"]
        industries = ["Bank", "Health", "Retail", "Manufacturing", "Energy", "Logistics", "Software"]
        rows = []
        for index in range(1, self.config.customers + 1):
            region = regions[(index + rng.randrange(len(regions))) % len(regions)]
            industry = industries[(index + rng.randrange(len(industries))) % len(industries)]
            name = f"{region['region_name']} {industry} Customer {index:03d}"
            rows.append(
                {
                    "customer_id": self._id(context, "customers", name),
                    "customer_name": name,
                    "region_id": region["region_id"],
                    "business_unit_id": bu_id if index % 10 else None,
                    "customer_segment": segments[(index + rng.randrange(len(segments))) % len(segments)],
                    "active_flag": True,
                }
            )
        return rows

    def _suppliers(
        self,
        context: RunContext,
        rng: Random,
        regions: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        categories = [
            "cloud infrastructure",
            "software",
            "contractor/services",
            "marketing",
            "facilities",
        ]
        currencies = ["USD", "AUD", "EUR", "GBP", "JPY"]
        rows = []
        for index in range(1, self.config.suppliers + 1):
            category = categories[(index - 1) % len(categories)]
            region = regions[(index + rng.randrange(len(regions))) % len(regions)]
            name = f"{category.title()} Supplier {index:02d}"
            rows.append(
                {
                    "supplier_id": self._id(context, "suppliers", name),
                    "supplier_name": name,
                    "supplier_category": category,
                    "region_id": region["region_id"],
                    "currency_code": currencies[(index + rng.randrange(len(currencies))) % len(currencies)],
                    "active_flag": True,
                }
            )
        return rows

    def _employees(
        self,
        context: RunContext,
        rng: Random,
        business_units: list[dict[str, object]],
        regions: list[dict[str, object]],
        departments: list[dict[str, object]],
        cost_centres: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        dept_by_id = {row["department_id"]: row["department_name"] for row in departments}
        cc_choices = cost_centres
        rows = []
        for index in range(1, self.config.employees + 1):
            cost_centre = cc_choices[(index + rng.randrange(len(cc_choices))) % len(cc_choices)]
            department_name = dept_by_id[cost_centre["department_id"]]
            region = regions[(index + rng.randrange(len(regions))) % len(regions)]
            business_unit_id = cost_centre["business_unit_id"]
            normalized_department = department_name.removeprefix("Atlas ")
            if business_unit_id is None and normalized_department in {"Finance", "People", "Operations", "Executive"}:
                business_unit_id = None
            elif business_unit_id is None:
                business_unit_id = business_units[2]["business_unit_id"]
            rows.append(
                {
                    "employee_id": self._id(context, "employees", f"employee-{index:03d}"),
                    "employee_name": f"Employee {index:03d}",
                    "role_title": self._role_for_department(normalized_department, index),
                    "business_unit_id": business_unit_id,
                    "region_id": region["region_id"],
                    "department_id": cost_centre["department_id"],
                    "cost_centre_id": cost_centre["cost_centre_id"],
                    "manager_employee_id": None,
                    "employment_status": "ACTIVE",
                    "start_date": date(2022 + (index % 3), ((index - 1) % 12) + 1, 1),
                    "end_date": None,
                    "source_system": SOURCE_SYSTEM,
                    "ingestion_batch_id": context.batch_id,
                    "record_version": 1,
                    "is_deleted": False,
                }
            )
        return rows

    def _role_for_department(self, department_name: str, index: int) -> str:
        roles = {
            "Sales": ["Account Executive", "Sales Manager", "Revenue Operations Analyst"],
            "Marketing": ["Demand Generation Manager", "Marketing Operations Specialist"],
            "Customer Success": ["Customer Success Manager", "Support Lead"],
            "Product": ["Product Manager", "Product Operations Analyst"],
            "Engineering": ["Software Engineer", "Platform Engineer", "Engineering Manager"],
            "Professional Services Delivery": ["Consultant", "Delivery Manager", "Solutions Architect"],
            "Finance": ["FP&A Analyst", "Finance Manager"],
            "People": ["People Partner", "Recruiting Specialist"],
            "Operations": ["Operations Manager", "Business Operations Analyst"],
            "Executive": ["Executive"],
        }
        choices = roles[department_name]
        return choices[index % len(choices)]

    def _manager_assignments(
        self,
        cost_centres: list[dict[str, object]],
        employees: list[dict[str, object]],
    ) -> list[dict[str, int]]:
        assignments = []
        for cost_centre in cost_centres:
            candidates = [
                employee
                for employee in employees
                if employee["cost_centre_id"] == cost_centre["cost_centre_id"]
            ]
            if candidates:
                manager = candidates[0]
                assignments.append(
                    {
                        "cost_centre_id": int(cost_centre["cost_centre_id"]),
                        "manager_employee_id": int(manager["employee_id"]),
                    }
                )
        return assignments
