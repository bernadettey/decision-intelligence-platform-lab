from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from random import Random

from generator.context import RunContext
from generator.ids import deterministic_int_id

SOURCE_SYSTEM = "synthetic_saas_commercial_generator"


@dataclass(frozen=True)
class MasterReference:
    business_unit_id: int
    regions: list[dict[str, object]]
    customers: list[dict[str, object]]
    products: list[dict[str, object]]
    currency_code: str = "USD"


@dataclass(frozen=True)
class SaaSCommercialConfig:
    subscriptions: int = 60


@dataclass(frozen=True)
class SaaSCommercialPopulation:
    customer_contracts: list[dict[str, object]]
    subscriptions: list[dict[str, object]]
    subscription_events: list[dict[str, object]]

    @property
    def row_counts(self) -> dict[str, int]:
        return {
            "customer_contracts": len(self.customer_contracts),
            "subscriptions": len(self.subscriptions),
            "subscription_events": len(self.subscription_events),
        }

    @property
    def total_rows(self) -> int:
        return sum(self.row_counts.values())


class SaaSCommercialGenerator:
    """Builds deterministic SaaS contract, subscription, and ARR movement rows."""

    def __init__(self, config: SaaSCommercialConfig | None = None) -> None:
        self.config = config or SaaSCommercialConfig()

    def generate(self, context: RunContext, reference: MasterReference) -> SaaSCommercialPopulation:
        if not reference.customers:
            raise ValueError("SaaS commercial generation requires bootstrapped customers")
        if not reference.products:
            raise ValueError("SaaS commercial generation requires SaaS products")
        if not reference.regions:
            raise ValueError("SaaS commercial generation requires regions")

        rng = Random(f"{context.random_seed}:{context.generator_version}:saas-commercial:{context.simulation_date}")
        customer_contracts = []
        subscriptions = []
        subscription_events = []

        for index in range(1, self.config.subscriptions + 1):
            customer = reference.customers[(index + rng.randrange(len(reference.customers))) % len(reference.customers)]
            product = reference.products[(index + rng.randrange(len(reference.products))) % len(reference.products)]
            region_id = int(customer["region_id"] or reference.regions[index % len(reference.regions)]["region_id"])
            contract_key = f"saas-contract-{context.simulation_date}-{index:03d}"
            subscription_key = f"saas-subscription-{context.simulation_date}-{index:03d}"
            arr_amount = self._arr_amount(index, product["product_family"])
            start_date = date(context.simulation_date.year, ((index - 1) % 12) + 1, 1)
            end_date = date(start_date.year + 1, start_date.month, 1)

            contract_id = self._id(context, "customer_contracts", contract_key)
            subscription_id = self._id(context, "subscriptions", subscription_key)
            event_id = self._id(context, "subscription_events", f"{subscription_key}-new")

            customer_contracts.append(
                {
                    "contract_id": contract_id,
                    "customer_id": customer["customer_id"],
                    "contract_type": "SAAS",
                    "contract_start_date": start_date,
                    "contract_end_date": end_date,
                    "contract_value": arr_amount,
                    "currency_code": reference.currency_code,
                    "business_unit_id": reference.business_unit_id,
                    "region_id": region_id,
                    "contract_status": "ACTIVE",
                    "source_system": SOURCE_SYSTEM,
                    "ingestion_batch_id": context.batch_id,
                    "record_version": 1,
                    "is_deleted": False,
                }
            )
            subscriptions.append(
                {
                    "subscription_id": subscription_id,
                    "contract_id": contract_id,
                    "customer_id": customer["customer_id"],
                    "product_id": product["product_id"],
                    "business_unit_id": reference.business_unit_id,
                    "region_id": region_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "billing_frequency": "ANNUAL" if index % 4 else "QUARTERLY",
                    "arr_amount": arr_amount,
                    "mrr_amount": (arr_amount / Decimal("12.00")).quantize(Decimal("0.01")),
                    "subscription_status": "ACTIVE",
                    "source_system": SOURCE_SYSTEM,
                    "ingestion_batch_id": context.batch_id,
                    "record_version": 1,
                    "is_deleted": False,
                }
            )
            subscription_events.append(
                {
                    "subscription_event_id": event_id,
                    "subscription_id": subscription_id,
                    "customer_id": customer["customer_id"],
                    "product_id": product["product_id"],
                    "event_date": start_date,
                    "event_type": "NEW",
                    "arr_delta": arr_amount,
                    "mrr_delta": (arr_amount / Decimal("12.00")).quantize(Decimal("0.01")),
                    "event_reason": "New SaaS subscription generated from deterministic bootstrap",
                    "source_system": SOURCE_SYSTEM,
                    "ingestion_batch_id": context.batch_id,
                }
            )

        return SaaSCommercialPopulation(
            customer_contracts=customer_contracts,
            subscriptions=subscriptions,
            subscription_events=subscription_events,
        )

    def _id(self, context: RunContext, table: str, key: str) -> int:
        return deterministic_int_id(
            "saas-commercial",
            context.random_seed,
            context.generator_version,
            context.simulation_date,
            table,
            key,
        )

    def _arr_amount(self, index: int, product_family: object) -> Decimal:
        base_amounts = {
            "SAAS_SUBSCRIPTION": [Decimal("24000.00"), Decimal("60000.00"), Decimal("120000.00")],
            "SAAS_ADDON": [Decimal("6000.00"), Decimal("12000.00"), Decimal("24000.00")],
        }
        family = str(product_family)
        amounts = base_amounts.get(family, [Decimal("24000.00")])
        return amounts[index % len(amounts)]
