from decimal import Decimal

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from app.repositories.postgres_read_repository import PostgresReadRepository
from app.services.ai_service import AIService
from app.services.query_service import QueryService


def test_query_service_uses_v1_schema_qualified_tables() -> None:
    sql, params = QueryService().build_variance_query("What is SaaS ARR?")

    assert params == {}
    assert "operations.subscriptions" in sql
    assert "operations.customer_contracts" in sql
    assert "master.business_units" in sql
    assert "FROM actuals" not in sql
    assert "JOIN budgets" not in sql
    assert "JOIN business_units bu ON bu.id" not in sql


def test_mock_ai_commentary_supports_v1_saas_summary_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    service = AIService()
    monkeypatch.setattr(service.settings, "openai_api_key", None)

    commentary = service.generate_commentary(
        "What is SaaS ARR?",
        ["operating_profit", "budget_variance"],
        [
            {
                "business_unit": "SaaS",
                "region": "APAC",
                "active_subscriptions": 2,
                "subscription_events": 2,
                "arr_amount": Decimal("120000.00"),
                "mrr_amount": Decimal("10000.00"),
            }
        ],
    )

    assert "active SaaS subscriptions" in commentary
    assert "schema-qualified SaaS commercial tables" in commentary


def test_postgres_read_repository_reads_current_v1_saas_schema() -> None:
    session = SessionLocal()
    ids = {
        "batch_id": None,
        "business_unit_id": 700001,
        "region_id": 700002,
        "customer_id": 700003,
        "product_id": 700004,
        "contract_id": 700005,
        "subscription_id": 700006,
        "subscription_event_id": 700007,
        "second_subscription_event_id": 700008,
    }
    try:
        try:
            session.execute(text("SELECT 1"))
            session.rollback()
        except SQLAlchemyError as exc:
            pytest.skip(f"PostgreSQL test database is unavailable: {exc}")

        cleanup_v1_probe_rows(session, ids)
        ids["batch_id"] = insert_v1_saas_probe_rows(session, ids)

        rows = PostgresReadRepository(session).fetch_saas_commercial_summary()
        probe_row = next(row for row in rows if row["business_unit"] == "Data Layer Probe SaaS")

        assert probe_row["region"] == "Data Layer Probe APAC"
        assert probe_row["active_contracts"] == 1
        assert probe_row["active_subscriptions"] == 1
        assert probe_row["subscription_events"] == 2
        assert probe_row["arr_amount"] == Decimal("120000.00")
        assert probe_row["mrr_amount"] == Decimal("10000.00")
        assert probe_row["arr_event_delta"] == Decimal("150000.00")
    finally:
        session.rollback()
        cleanup_v1_probe_rows(session, ids)
        session.close()


def insert_v1_saas_probe_rows(session, ids: dict[str, int | None]) -> int:
    batch_id = session.execute(
        text(
            """
            INSERT INTO operations.ingestion_batches (
                simulation_id,
                simulation_date,
                batch_type,
                status,
                generator_version
            )
            VALUES (1, '2024-12-31', 'BOOTSTRAP', 'SUCCEEDED', 'm1.4-data-layer-test')
            RETURNING batch_id
            """
        )
    ).scalar_one()
    session.execute(
        text(
            """
            INSERT INTO master.business_units (
                business_unit_id,
                business_unit_name,
                active_flag
            )
            VALUES (:business_unit_id, 'Data Layer Probe SaaS', true)
            """
        ),
        ids,
    )
    session.execute(
        text(
            """
            INSERT INTO master.regions (region_id, region_name, active_flag)
            VALUES (:region_id, 'Data Layer Probe APAC', true)
            """
        ),
        ids,
    )
    session.execute(
        text(
            """
            INSERT INTO master.currencies (currency_code, currency_name, active_flag)
            VALUES ('USD', 'US Dollar', true)
            ON CONFLICT (currency_code) DO NOTHING
            """
        )
    )
    session.execute(
        text(
            """
            INSERT INTO master.customers (
                customer_id,
                customer_name,
                region_id,
                business_unit_id,
                customer_segment,
                active_flag
            )
            VALUES (
                :customer_id,
                'Data Layer Probe Customer',
                :region_id,
                :business_unit_id,
                'Enterprise',
                true
            )
            """
        ),
        ids,
    )
    session.execute(
        text(
            """
            INSERT INTO master.products (
                product_id,
                product_name,
                product_family,
                business_unit_id,
                active_flag
            )
            VALUES (
                :product_id,
                'Data Layer Probe Platform',
                'SAAS_SUBSCRIPTION',
                :business_unit_id,
                true
            )
            """
        ),
        ids,
    )
    params = {**ids, "batch_id": batch_id}
    session.execute(
        text(
            """
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
                contract_status,
                source_system,
                ingestion_batch_id
            )
            VALUES (
                :contract_id,
                :customer_id,
                'SAAS',
                '2024-01-01',
                '2024-12-31',
                120000.00,
                'USD',
                :business_unit_id,
                :region_id,
                'ACTIVE',
                'm1.4_data_layer_test',
                :batch_id
            )
            """
        ),
        params,
    )
    session.execute(
        text(
            """
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
                subscription_status,
                source_system,
                ingestion_batch_id
            )
            VALUES (
                :subscription_id,
                :contract_id,
                :customer_id,
                :product_id,
                :business_unit_id,
                :region_id,
                '2024-01-01',
                '2024-12-31',
                'ANNUAL',
                120000.00,
                10000.00,
                'ACTIVE',
                'm1.4_data_layer_test',
                :batch_id
            )
            """
        ),
        params,
    )
    session.execute(
        text(
            """
            INSERT INTO operations.subscription_events (
                subscription_event_id,
                subscription_id,
                customer_id,
                product_id,
                event_date,
                event_type,
                arr_delta,
                mrr_delta,
                event_reason,
                source_system,
                ingestion_batch_id
            )
            VALUES (
                :subscription_event_id,
                :subscription_id,
                :customer_id,
                :product_id,
                '2024-01-01',
                'NEW',
                120000.00,
                10000.00,
                'Data layer probe',
                'm1.4_data_layer_test',
                :batch_id
            )
            """
        ),
        params,
    )
    session.execute(
        text(
            """
            INSERT INTO operations.subscription_events (
                subscription_event_id,
                subscription_id,
                customer_id,
                product_id,
                event_date,
                event_type,
                arr_delta,
                mrr_delta,
                event_reason,
                source_system,
                ingestion_batch_id
            )
            VALUES (
                :second_subscription_event_id,
                :subscription_id,
                :customer_id,
                :product_id,
                '2024-06-01',
                'EXPANSION',
                30000.00,
                2500.00,
                'Data layer fan-out probe',
                'm1.4_data_layer_test',
                :batch_id
            )
            """
        ),
        params,
    )
    session.commit()
    return int(batch_id)


def cleanup_v1_probe_rows(session, ids: dict[str, int | None]) -> None:
    session.rollback()
    session.execute(
        text(
            """
            DELETE FROM operations.subscription_events
            WHERE subscription_event_id IN (
                :subscription_event_id,
                :second_subscription_event_id
            )
            """
        ),
        ids,
    )
    session.execute(
        text("DELETE FROM operations.subscriptions WHERE subscription_id = :subscription_id"),
        ids,
    )
    session.execute(
        text("DELETE FROM operations.customer_contracts WHERE contract_id = :contract_id"),
        ids,
    )
    session.execute(text("DELETE FROM master.products WHERE product_id = :product_id"), ids)
    session.execute(text("DELETE FROM master.customers WHERE customer_id = :customer_id"), ids)
    session.execute(text("DELETE FROM master.regions WHERE region_id = :region_id"), ids)
    session.execute(text("DELETE FROM master.business_units WHERE business_unit_id = :business_unit_id"), ids)
    session.execute(
        text(
            """
            DELETE FROM operations.ingestion_batches
            WHERE generator_version = 'm1.4-data-layer-test'
            """
        )
    )
    session.commit()
