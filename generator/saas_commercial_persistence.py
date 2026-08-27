from sqlalchemy import text
from sqlalchemy.orm import Session

from generator.context import RunContext
from generator.saas_commercial_data import MasterReference, SaaSCommercialPopulation


class SaaSCommercialDataAlreadyExistsError(RuntimeError):
    """Raised when a deterministic SaaS commercial population already exists."""


class SaaSCommercialRepository:
    """Reads master references and persists SaaS operational rows."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def load_master_reference(self) -> MasterReference:
        business_unit_id = self.session.execute(
            text(
                """
                SELECT business_unit_id
                FROM master.business_units
                WHERE business_unit_name = 'SaaS'
                """
            )
        ).scalar_one()
        regions = [dict(row._mapping) for row in self.session.execute(text("SELECT region_id FROM master.regions ORDER BY region_id"))]
        customers = [
            dict(row._mapping)
            for row in self.session.execute(
                text(
                    """
                    SELECT customer_id, region_id
                    FROM master.customers
                    WHERE business_unit_id = :business_unit_id
                       OR business_unit_id IS NULL
                    ORDER BY customer_id
                    """
                ),
                {"business_unit_id": business_unit_id},
            )
        ]
        products = [
            dict(row._mapping)
            for row in self.session.execute(
                text(
                    """
                    SELECT product_id, product_family
                    FROM master.products
                    WHERE business_unit_id = :business_unit_id
                      AND product_family IN ('SAAS_SUBSCRIPTION', 'SAAS_ADDON')
                    ORDER BY product_id
                    """
                ),
                {"business_unit_id": business_unit_id},
            )
        ]
        currency_code = self.session.execute(
            text(
                """
                SELECT currency_code
                FROM master.currencies
                WHERE currency_code = 'USD'
                """
            )
        ).scalar_one()

        return MasterReference(
            business_unit_id=int(business_unit_id),
            regions=regions,
            customers=customers,
            products=products,
            currency_code=str(currency_code),
        )

    def bootstrap(self, context: RunContext, population: SaaSCommercialPopulation) -> int:
        if context.batch_id is None:
            raise ValueError("SaaS commercial bootstrap requires a started ingestion batch")

        self._assert_population_absent(population)
        self._insert_customer_contracts(population.customer_contracts)
        self._insert_subscriptions(population.subscriptions)
        self._insert_subscription_events(population.subscription_events)
        return population.total_rows

    def _assert_population_absent(self, population: SaaSCommercialPopulation) -> None:
        checks = [
            (
                "operations.customer_contracts",
                "contract_id",
                [row["contract_id"] for row in population.customer_contracts],
            ),
            ("operations.subscriptions", "subscription_id", [row["subscription_id"] for row in population.subscriptions]),
            (
                "operations.subscription_events",
                "subscription_event_id",
                [row["subscription_event_id"] for row in population.subscription_events],
            ),
        ]
        for table_name, column_name, values in checks:
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
                raise SaaSCommercialDataAlreadyExistsError(
                    f"{table_name} already contains {existing_count} generated key(s)"
                )

    def _insert_customer_contracts(self, rows: list[dict[str, object]]) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO operations.customer_contracts (
                    contract_id, customer_id, contract_type, contract_start_date,
                    contract_end_date, contract_value, currency_code,
                    business_unit_id, region_id, contract_status, source_system,
                    ingestion_batch_id, record_version, is_deleted
                )
                VALUES (
                    :contract_id, :customer_id, :contract_type, :contract_start_date,
                    :contract_end_date, :contract_value, :currency_code,
                    :business_unit_id, :region_id, :contract_status, :source_system,
                    :ingestion_batch_id, :record_version, :is_deleted
                )
                """
            ),
            rows,
        )

    def _insert_subscriptions(self, rows: list[dict[str, object]]) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO operations.subscriptions (
                    subscription_id, contract_id, customer_id, product_id,
                    business_unit_id, region_id, start_date, end_date,
                    billing_frequency, arr_amount, mrr_amount, subscription_status,
                    source_system, ingestion_batch_id, record_version, is_deleted
                )
                VALUES (
                    :subscription_id, :contract_id, :customer_id, :product_id,
                    :business_unit_id, :region_id, :start_date, :end_date,
                    :billing_frequency, :arr_amount, :mrr_amount, :subscription_status,
                    :source_system, :ingestion_batch_id, :record_version, :is_deleted
                )
                """
            ),
            rows,
        )

    def _insert_subscription_events(self, rows: list[dict[str, object]]) -> None:
        self.session.execute(
            text(
                """
                INSERT INTO operations.subscription_events (
                    subscription_event_id, subscription_id, customer_id,
                    product_id, event_date, event_type, arr_delta, mrr_delta,
                    event_reason, source_system, ingestion_batch_id
                )
                VALUES (
                    :subscription_event_id, :subscription_id, :customer_id,
                    :product_id, :event_date, :event_type, :arr_delta, :mrr_delta,
                    :event_reason, :source_system, :ingestion_batch_id
                )
                """
            ),
            rows,
        )
