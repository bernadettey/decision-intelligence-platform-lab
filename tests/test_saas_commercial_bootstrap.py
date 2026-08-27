from datetime import date

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from generator.context import RunContext, RunMode
from generator.master_bootstrap import build_master_bootstrap_runner
from generator.master_data import MasterDataGenerator, MasterDataPopulation
from generator.saas_commercial_bootstrap import build_saas_commercial_bootstrap_runner
from generator.saas_commercial_data import SaaSCommercialConfig, SaaSCommercialGenerator
from generator.saas_commercial_persistence import SaaSCommercialRepository


EXPECTED_SAAS_COUNTS = {
    "customer_contracts": 60,
    "subscriptions": 60,
    "subscription_events": 60,
}


def build_context(*, batch_id: int | None = 20, generator_version: str = "m1.3-phase3-test") -> RunContext:
    return RunContext(
        simulation_id=1,
        mode=RunMode.BOOTSTRAP,
        simulation_date=date(2024, 12, 31),
        random_seed=424242,
        generator_version=generator_version,
        batch_id=batch_id,
    )


def reference_from_master_population(context: RunContext):
    master = MasterDataGenerator().generate(context)
    business_unit_id = next(
        int(row["business_unit_id"])
        for row in master.business_units
        if row["business_unit_name"] == "SaaS"
    )
    products = [
        row
        for row in master.products
        if row["business_unit_id"] == business_unit_id
        and row["product_family"] in {"SAAS_SUBSCRIPTION", "SAAS_ADDON"}
    ]
    customers = [
        row
        for row in master.customers
        if row["business_unit_id"] in {business_unit_id, None}
    ]

    from generator.saas_commercial_data import MasterReference

    return MasterReference(
        business_unit_id=business_unit_id,
        regions=master.regions,
        customers=customers,
        products=products,
    )


def test_saas_commercial_generation_is_reproducible() -> None:
    context = build_context()
    reference = reference_from_master_population(context)
    generator = SaaSCommercialGenerator()

    first = generator.generate(context, reference)
    second = generator.generate(context, reference)
    changed_version = generator.generate(build_context(generator_version="m1.3-phase3-test-v2"), reference)

    assert first == second
    assert first.row_counts == EXPECTED_SAAS_COUNTS
    assert first.subscription_events == second.subscription_events
    assert first.customer_contracts != changed_version.customer_contracts


def test_saas_commercial_business_rules_are_coherent() -> None:
    context = build_context()
    reference = reference_from_master_population(context)
    population = SaaSCommercialGenerator().generate(context, reference)
    contract_ids = {row["contract_id"] for row in population.customer_contracts}
    subscription_ids = {row["subscription_id"] for row in population.subscriptions}
    saas_product_ids = {row["product_id"] for row in reference.products}

    assert all(row["contract_type"] == "SAAS" for row in population.customer_contracts)
    assert all(row["contract_status"] == "ACTIVE" for row in population.customer_contracts)
    assert all(row["business_unit_id"] == reference.business_unit_id for row in population.customer_contracts)
    assert all(row["contract_id"] in contract_ids for row in population.subscriptions)
    assert all(row["product_id"] in saas_product_ids for row in population.subscriptions)
    assert all(row["arr_amount"] > 0 for row in population.subscriptions)
    assert all(row["mrr_amount"] == row["arr_amount"] / 12 for row in population.subscriptions)
    assert all(row["event_type"] == "NEW" for row in population.subscription_events)
    assert all(row["subscription_id"] in subscription_ids for row in population.subscription_events)
    assert all(row["arr_delta"] > 0 for row in population.subscription_events)


def assert_postgres_available(session) -> None:
    try:
        session.execute(text("SELECT 1"))
        session.rollback()
    except SQLAlchemyError as exc:
        pytest.skip(f"PostgreSQL test database is unavailable: {exc}")


def cleanup_saas_population(session, generator_version: str) -> None:
    session.rollback()
    batch_ids = [
        row.batch_id
        for row in session.execute(
            text(
                """
                SELECT batch_id
                FROM operations.ingestion_batches
                WHERE generator_version = :generator_version
                """
            ),
            {"generator_version": generator_version},
        )
    ]
    if not batch_ids:
        return

    session.execute(
        text("DELETE FROM operations.subscription_events WHERE ingestion_batch_id = ANY(:batch_ids)"),
        {"batch_ids": batch_ids},
    )
    session.execute(
        text("DELETE FROM operations.subscriptions WHERE ingestion_batch_id = ANY(:batch_ids)"),
        {"batch_ids": batch_ids},
    )
    session.execute(
        text("DELETE FROM operations.customer_contracts WHERE ingestion_batch_id = ANY(:batch_ids)"),
        {"batch_ids": batch_ids},
    )
    session.execute(
        text(
            """
            UPDATE operations.simulation_control
            SET current_batch_id = NULL
            WHERE current_batch_id = ANY(:batch_ids)
            """
        ),
        {"batch_ids": batch_ids},
    )
    session.execute(
        text("DELETE FROM operations.ingestion_batches WHERE batch_id = ANY(:batch_ids)"),
        {"batch_ids": batch_ids},
    )
    session.commit()


def cleanup_master_population(session, population: MasterDataPopulation, generator_version: str) -> None:
    session.rollback()
    ids = {
        "business_unit_ids": [row["business_unit_id"] for row in population.business_units],
        "business_unit_names": [row["business_unit_name"] for row in population.business_units],
        "region_ids": [row["region_id"] for row in population.regions],
        "region_names": [row["region_name"] for row in population.regions],
        "department_ids": [row["department_id"] for row in population.departments],
        "department_names": [row["department_name"] for row in population.departments],
        "cost_centre_ids": [row["cost_centre_id"] for row in population.cost_centres],
        "cost_centre_names": [row["cost_centre_name"] for row in population.cost_centres],
        "gl_account_ids": [row["gl_account_id"] for row in population.gl_accounts],
        "account_codes": [row["account_code"] for row in population.gl_accounts],
        "product_ids": [row["product_id"] for row in population.products],
        "product_names": [row["product_name"] for row in population.products],
        "customer_ids": [row["customer_id"] for row in population.customers],
        "customer_names": [row["customer_name"] for row in population.customers],
        "supplier_ids": [row["supplier_id"] for row in population.suppliers],
        "supplier_names": [row["supplier_name"] for row in population.suppliers],
        "employee_ids": [row["employee_id"] for row in population.employees],
        "employee_names": [row["employee_name"] for row in population.employees],
    }
    statements = [
        (
            """
            UPDATE master.cost_centres
            SET manager_employee_id = NULL
            WHERE cost_centre_id = ANY(:cost_centre_ids)
               OR cost_centre_name = ANY(:cost_centre_names)
            """,
            ids,
        ),
        ("DELETE FROM master.employees WHERE employee_id = ANY(:employee_ids) OR employee_name = ANY(:employee_names)", ids),
        ("DELETE FROM master.customers WHERE customer_id = ANY(:customer_ids) OR customer_name = ANY(:customer_names)", ids),
        ("DELETE FROM master.suppliers WHERE supplier_id = ANY(:supplier_ids) OR supplier_name = ANY(:supplier_names)", ids),
        ("DELETE FROM master.products WHERE product_id = ANY(:product_ids) OR product_name = ANY(:product_names)", ids),
        ("DELETE FROM master.cost_centres WHERE cost_centre_id = ANY(:cost_centre_ids) OR cost_centre_name = ANY(:cost_centre_names)", ids),
        ("DELETE FROM master.gl_accounts WHERE gl_account_id = ANY(:gl_account_ids) OR account_code = ANY(:account_codes)", ids),
        ("DELETE FROM master.departments WHERE department_id = ANY(:department_ids) OR department_name = ANY(:department_names)", ids),
        ("DELETE FROM master.regions WHERE region_id = ANY(:region_ids) OR region_name = ANY(:region_names)", ids),
        ("DELETE FROM master.business_units WHERE business_unit_id = ANY(:business_unit_ids) OR business_unit_name = ANY(:business_unit_names)", ids),
        (
            """
            UPDATE operations.simulation_control
            SET current_batch_id = NULL
            WHERE current_batch_id IN (
                SELECT batch_id
                FROM operations.ingestion_batches
                WHERE generator_version = :generator_version
            )
            """,
            {"generator_version": generator_version},
        ),
        (
            "DELETE FROM operations.ingestion_batches WHERE generator_version = :generator_version",
            {"generator_version": generator_version},
        ),
    ]
    for statement, params in statements:
        session.execute(text(statement), params)
    session.commit()


def ensure_master_bootstrap(session) -> tuple[MasterDataPopulation | None, str]:
    generator_version = "m1.3-phase2-test-master-for-saas"
    if session.execute(text("SELECT count(*) FROM master.customers")).scalar_one():
        session.rollback()
        return None, generator_version

    runner = build_master_bootstrap_runner(session)
    context = runner.build_context(
        simulation_id=1,
        mode=RunMode.BOOTSTRAP,
        generator_version=generator_version,
        target_simulation_date=date(2024, 12, 31),
    )
    runner.run(context)
    return MasterDataGenerator().generate(
        build_context(batch_id=None, generator_version=generator_version)
    ), generator_version


def test_saas_commercial_bootstrap_persists_valid_fk_chain() -> None:
    session = SessionLocal()
    generator_version = "m1.3-phase3-integration-test"
    created_master: tuple[MasterDataPopulation | None, str] = (None, "")
    original_clock: date | None = None
    original_batch_id: int | None = None
    try:
        assert_postgres_available(session)
        cleanup_saas_population(session, generator_version)
        original_clock, original_batch_id = session.execute(
            text(
                """
                SELECT current_simulation_date, current_batch_id
                FROM operations.simulation_control
                WHERE simulation_id = 1
                """
            )
        ).one()
        created_master = ensure_master_bootstrap(session)

        runner = build_saas_commercial_bootstrap_runner(session)
        context = runner.build_context(
            simulation_id=1,
            mode=RunMode.BOOTSTRAP,
            generator_version=generator_version,
            target_simulation_date=date(2024, 12, 31),
        )
        batch_id = runner.run(context)

        counts = dict(
            session.execute(
                text(
                    """
                    SELECT 'customer_contracts' AS table_name, count(*) AS row_count
                    FROM operations.customer_contracts
                    WHERE ingestion_batch_id = :batch_id
                    UNION ALL
                    SELECT 'subscriptions', count(*)
                    FROM operations.subscriptions
                    WHERE ingestion_batch_id = :batch_id
                    UNION ALL
                    SELECT 'subscription_events', count(*)
                    FROM operations.subscription_events
                    WHERE ingestion_batch_id = :batch_id
                    """
                ),
                {"batch_id": batch_id},
            ).all()
        )
        invalid_product_count = session.execute(
            text(
                """
                SELECT count(*)
                FROM operations.subscriptions s
                JOIN master.products p ON p.product_id = s.product_id
                WHERE s.ingestion_batch_id = :batch_id
                  AND p.product_family NOT IN ('SAAS_SUBSCRIPTION', 'SAAS_ADDON')
                """
            ),
            {"batch_id": batch_id},
        ).scalar_one()
        event_mismatch_count = session.execute(
            text(
                """
                SELECT count(*)
                FROM operations.subscription_events se
                LEFT JOIN operations.subscriptions s
                  ON s.subscription_id = se.subscription_id
                WHERE se.ingestion_batch_id = :batch_id
                  AND (
                    s.subscription_id IS NULL
                    OR se.customer_id <> s.customer_id
                    OR se.product_id <> s.product_id
                  )
                """
            ),
            {"batch_id": batch_id},
        ).scalar_one()
        batch = session.execute(
            text(
                """
                SELECT status, records_generated
                FROM operations.ingestion_batches
                WHERE batch_id = :batch_id
                """
            ),
            {"batch_id": batch_id},
        ).one()

        assert counts == EXPECTED_SAAS_COUNTS
        assert invalid_product_count == 0
        assert event_mismatch_count == 0
        assert batch.status == "SUCCEEDED"
        assert batch.records_generated == sum(EXPECTED_SAAS_COUNTS.values())
    finally:
        session.rollback()
        cleanup_saas_population(session, generator_version)
        if created_master[0] is not None:
            cleanup_master_population(session, created_master[0], created_master[1])
        if original_clock is not None:
            session.execute(
                text(
                    """
                    UPDATE operations.simulation_control
                    SET current_simulation_date = :current_simulation_date,
                        current_batch_id = :current_batch_id
                    WHERE simulation_id = 1
                    """
                ),
                {"current_simulation_date": original_clock, "current_batch_id": original_batch_id},
            )
            session.commit()
        session.close()


def test_failed_saas_commercial_bootstrap_rolls_back_rows() -> None:
    session = SessionLocal()
    generator_version = "m1.3-phase3-failure-test"
    created_master: tuple[MasterDataPopulation | None, str] = (None, "")
    original_clock: date | None = None
    try:
        assert_postgres_available(session)
        cleanup_saas_population(session, generator_version)
        created_master = ensure_master_bootstrap(session)
        original_clock = session.execute(
            text("SELECT current_simulation_date FROM operations.simulation_control WHERE simulation_id = 1")
        ).scalar_one()
        repository = SaaSCommercialRepository(session)
        data_generator = SaaSCommercialGenerator()

        def failing_step(context: RunContext) -> int:
            population = data_generator.generate(context, repository.load_master_reference())
            repository.bootstrap(context, population)
            raise RuntimeError("SaaS commercial probe failed")

        from generator.repository import SqlAlchemySimulationRepository, SqlAlchemyTransactionManager
        from generator.runner import SimulationRunner

        simulation_repository = SqlAlchemySimulationRepository(session)
        runner = SimulationRunner(
            batch_repository=simulation_repository,
            clock_repository=simulation_repository,
            transaction_manager=SqlAlchemyTransactionManager(session),
            generator_step=failing_step,
        )
        context = runner.build_context(
            simulation_id=1,
            mode=RunMode.BOOTSTRAP,
            generator_version=generator_version,
            target_simulation_date=date(2024, 12, 31),
        )

        with pytest.raises(RuntimeError, match="SaaS commercial probe failed"):
            runner.run(context)

        batch_id = session.execute(
            text(
                """
                SELECT max(batch_id)
                FROM operations.ingestion_batches
                WHERE generator_version = :generator_version
                """
            ),
            {"generator_version": generator_version},
        ).scalar_one()
        failed_batch = session.execute(
            text(
                """
                SELECT status, error_message
                FROM operations.ingestion_batches
                WHERE batch_id = :batch_id
                """
            ),
            {"batch_id": batch_id},
        ).one()
        generated_contracts = session.execute(
            text("SELECT count(*) FROM operations.customer_contracts WHERE ingestion_batch_id = :batch_id"),
            {"batch_id": batch_id},
        ).scalar_one()
        current_clock = session.execute(
            text("SELECT current_simulation_date FROM operations.simulation_control WHERE simulation_id = 1")
        ).scalar_one()

        assert failed_batch.status == "FAILED"
        assert failed_batch.error_message == "RuntimeError: SaaS commercial probe failed"
        assert generated_contracts == 0
        assert current_clock == original_clock
    finally:
        session.rollback()
        cleanup_saas_population(session, generator_version)
        if created_master[0] is not None:
            cleanup_master_population(session, created_master[0], created_master[1])
        session.close()


def test_repeated_saas_commercial_bootstrap_fails_without_duplicates() -> None:
    session = SessionLocal()
    generator_version = "m1.3-phase3-repeat-test"
    created_master: tuple[MasterDataPopulation | None, str] = (None, "")
    original_clock: date | None = None
    original_batch_id: int | None = None
    try:
        assert_postgres_available(session)
        cleanup_saas_population(session, generator_version)
        original_clock, original_batch_id = session.execute(
            text(
                """
                SELECT current_simulation_date, current_batch_id
                FROM operations.simulation_control
                WHERE simulation_id = 1
                """
            )
        ).one()
        created_master = ensure_master_bootstrap(session)

        first_runner = build_saas_commercial_bootstrap_runner(session)
        first_context = first_runner.build_context(
            simulation_id=1,
            mode=RunMode.BOOTSTRAP,
            generator_version=generator_version,
            target_simulation_date=date(2024, 12, 31),
        )
        first_batch_id = first_runner.run(first_context)

        second_runner = build_saas_commercial_bootstrap_runner(session)
        second_context = second_runner.build_context(
            simulation_id=1,
            mode=RunMode.BOOTSTRAP,
            generator_version=generator_version,
            target_simulation_date=date(2024, 12, 31),
        )
        with pytest.raises(RuntimeError, match="already contains"):
            second_runner.run(second_context)

        assert session.execute(
            text("SELECT count(*) FROM operations.subscriptions WHERE ingestion_batch_id = :batch_id"),
            {"batch_id": first_batch_id},
        ).scalar_one() == EXPECTED_SAAS_COUNTS["subscriptions"]
        assert session.execute(
            text(
                """
                SELECT count(*)
                FROM operations.ingestion_batches
                WHERE generator_version = :generator_version
                  AND status = 'FAILED'
                """
            ),
            {"generator_version": generator_version},
        ).scalar_one() == 1
    finally:
        session.rollback()
        cleanup_saas_population(session, generator_version)
        if created_master[0] is not None:
            cleanup_master_population(session, created_master[0], created_master[1])
        if original_clock is not None:
            session.execute(
                text(
                    """
                    UPDATE operations.simulation_control
                    SET current_simulation_date = :current_simulation_date,
                        current_batch_id = :current_batch_id
                    WHERE simulation_id = 1
                    """
                ),
                {"current_simulation_date": original_clock, "current_batch_id": original_batch_id},
            )
            session.commit()
        session.close()
