from datetime import date

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from generator.context import RunContext, RunMode
from generator.master_bootstrap import build_master_bootstrap_runner
from generator.master_data import MasterDataGenerator, MasterDataPopulation
from generator.master_persistence import MasterDataRepository
from generator.repository import SqlAlchemySimulationRepository, SqlAlchemyTransactionManager
from generator.runner import SimulationRunner


EXPECTED_MASTER_COUNTS = {
    "business_units": 3,
    "regions": 3,
    "departments": 10,
    "cost_centres": 15,
    "currencies": 5,
    "gl_accounts": 24,
    "products": 8,
    "customers": 100,
    "suppliers": 30,
    "employees": 100,
}


def build_context(*, batch_id: int | None = 10, generator_version: str = "m1.3-phase2-test") -> RunContext:
    return RunContext(
        simulation_id=1,
        mode=RunMode.BOOTSTRAP,
        simulation_date=date(2024, 12, 31),
        random_seed=424242,
        generator_version=generator_version,
        batch_id=batch_id,
    )


def test_master_generation_is_reproducible() -> None:
    generator = MasterDataGenerator()
    first = generator.generate(build_context())
    second = generator.generate(build_context())
    changed_version = generator.generate(build_context(generator_version="m1.3-phase2-test-v2"))

    assert first == second
    assert first.row_counts == EXPECTED_MASTER_COUNTS
    assert first.business_units != changed_version.business_units


def test_generated_organization_relationships_are_coherent() -> None:
    population = MasterDataGenerator().generate(build_context())

    business_unit_ids = {row["business_unit_id"] for row in population.business_units}
    region_ids = {row["region_id"] for row in population.regions}
    department_ids = {row["department_id"] for row in population.departments}
    cost_centre_ids = {row["cost_centre_id"] for row in population.cost_centres}
    employee_ids = {row["employee_id"] for row in population.employees}

    assert any(row["business_unit_id"] is None for row in population.cost_centres)
    assert all(
        row["business_unit_id"] is None or row["business_unit_id"] in business_unit_ids
        for row in population.cost_centres
    )
    assert all(row["department_id"] in department_ids for row in population.cost_centres)
    assert all(row["region_id"] in region_ids for row in population.customers)
    assert all(row["region_id"] in region_ids for row in population.employees)
    assert all(row["cost_centre_id"] in cost_centre_ids for row in population.employees)
    assert all(row["department_id"] in department_ids for row in population.employees)
    assert all(row["manager_employee_id"] is None for row in population.cost_centres)
    assert all(
        row["cost_centre_id"] in cost_centre_ids and row["manager_employee_id"] in employee_ids
        for row in population.manager_assignments
    )


def assert_postgres_available(session) -> None:
    try:
        session.execute(text("SELECT 1"))
        session.rollback()
    except SQLAlchemyError as exc:
        pytest.skip(f"PostgreSQL test database is unavailable: {exc}")


def cleanup_population(session, population: MasterDataPopulation, generator_version: str) -> None:
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


def generated_table_count(session, table_name: str, id_column: str, values: list[object]) -> int:
    return int(
        session.execute(
            text(f"SELECT count(*) FROM master.{table_name} WHERE {id_column} = ANY(:values)"),
            {"values": values},
        ).scalar_one()
    )


def test_master_bootstrap_runs_through_simulation_lifecycle() -> None:
    session = SessionLocal()
    generator_version = "m1.3-phase2-test"
    population = MasterDataGenerator().generate(build_context(generator_version=generator_version))
    original_clock: date | None = None
    original_batch_id: int | None = None
    try:
        assert_postgres_available(session)
        cleanup_population(session, population, generator_version)
        original_clock, original_batch_id = session.execute(
            text(
                """
                SELECT current_simulation_date, current_batch_id
                FROM operations.simulation_control
                WHERE simulation_id = 1
                """
            )
        ).one()

        runner = build_master_bootstrap_runner(session)
        context = runner.build_context(
            simulation_id=1,
            mode=RunMode.BOOTSTRAP,
            generator_version=generator_version,
            target_simulation_date=date(2024, 12, 31),
        )

        batch_id = runner.run(context)

        counts = {
            "business_units": generated_table_count(session, "business_units", "business_unit_id", [row["business_unit_id"] for row in population.business_units]),
            "regions": generated_table_count(session, "regions", "region_id", [row["region_id"] for row in population.regions]),
            "departments": generated_table_count(session, "departments", "department_id", [row["department_id"] for row in population.departments]),
            "cost_centres": generated_table_count(session, "cost_centres", "cost_centre_id", [row["cost_centre_id"] for row in population.cost_centres]),
            "currencies": int(session.execute(text("SELECT count(*) FROM master.currencies WHERE currency_code = ANY(:values)"), {"values": [row["currency_code"] for row in population.currencies]}).scalar_one()),
            "gl_accounts": generated_table_count(session, "gl_accounts", "gl_account_id", [row["gl_account_id"] for row in population.gl_accounts]),
            "products": generated_table_count(session, "products", "product_id", [row["product_id"] for row in population.products]),
            "customers": generated_table_count(session, "customers", "customer_id", [row["customer_id"] for row in population.customers]),
            "suppliers": generated_table_count(session, "suppliers", "supplier_id", [row["supplier_id"] for row in population.suppliers]),
            "employees": generated_table_count(session, "employees", "employee_id", [row["employee_id"] for row in population.employees]),
        }
        batch = session.execute(
            text(
                """
                SELECT status, records_generated, generator_version
                FROM operations.ingestion_batches
                WHERE batch_id = :batch_id
                """
            ),
            {"batch_id": batch_id},
        ).one()
        clock = session.execute(
            text(
                """
                SELECT current_simulation_date, current_batch_id
                FROM operations.simulation_control
                WHERE simulation_id = 1
                """
            )
        ).one()
        employee_metadata = session.execute(
            text(
                """
                SELECT count(*)
                FROM master.employees
                WHERE ingestion_batch_id = :batch_id
                  AND source_system = 'synthetic_master_bootstrap'
                  AND record_version = 1
                  AND is_deleted = false
                """
            ),
            {"batch_id": batch_id},
        ).scalar_one()
        manager_count = session.execute(
            text(
                """
                SELECT count(*)
                FROM master.cost_centres
                WHERE cost_centre_id = ANY(:cost_centre_ids)
                  AND manager_employee_id IS NOT NULL
                """
            ),
            {"cost_centre_ids": [row["cost_centre_id"] for row in population.cost_centres]},
        ).scalar_one()
        orphan_count = session.execute(
            text(
                """
                SELECT count(*)
                FROM master.cost_centres cc
                LEFT JOIN master.employees e
                  ON e.employee_id = cc.manager_employee_id
                WHERE cc.cost_centre_id = ANY(:cost_centre_ids)
                  AND cc.manager_employee_id IS NOT NULL
                  AND e.employee_id IS NULL
                """
            ),
            {"cost_centre_ids": [row["cost_centre_id"] for row in population.cost_centres]},
        ).scalar_one()

        assert counts == EXPECTED_MASTER_COUNTS
        assert batch.status == "SUCCEEDED"
        assert batch.records_generated == sum(EXPECTED_MASTER_COUNTS.values())
        assert batch.generator_version == generator_version
        assert clock.current_simulation_date == date(2024, 12, 31)
        assert clock.current_batch_id == batch_id
        assert employee_metadata == EXPECTED_MASTER_COUNTS["employees"]
        assert manager_count > 0
        assert orphan_count == 0
    finally:
        session.rollback()
        cleanup_population(session, population, generator_version)
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


def test_failed_master_bootstrap_rolls_back_rows_and_persists_failed_batch() -> None:
    session = SessionLocal()
    generator_version = "m1.3-phase2-failure-test"
    population = MasterDataGenerator().generate(build_context(generator_version=generator_version))
    batch_id: int | None = None
    original_clock: date | None = None
    try:
        assert_postgres_available(session)
        cleanup_population(session, population, generator_version)
        original_clock = session.execute(
            text("SELECT current_simulation_date FROM operations.simulation_control WHERE simulation_id = 1")
        ).scalar_one()
        data_generator = MasterDataGenerator()
        master_repository = MasterDataRepository(session)
        simulation_repository = SqlAlchemySimulationRepository(session)

        def failing_step(context: RunContext) -> int:
            generated_population = data_generator.generate(context)
            master_repository.bootstrap(context, generated_population)
            raise RuntimeError("master bootstrap probe failed")

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

        with pytest.raises(RuntimeError, match="master bootstrap probe failed"):
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
        batch = session.execute(
            text(
                """
                SELECT status, error_message
                FROM operations.ingestion_batches
                WHERE batch_id = :batch_id
                """
            ),
            {"batch_id": batch_id},
        ).one()
        clock = session.execute(
            text(
                """
                SELECT current_simulation_date, current_batch_id
                FROM operations.simulation_control
                WHERE simulation_id = 1
                """
            )
        ).one()

        assert batch.status == "FAILED"
        assert batch.error_message == "RuntimeError: master bootstrap probe failed"
        assert clock.current_simulation_date == original_clock
        assert all(
            generated_table_count(
                session,
                table,
                id_column,
                [row[id_column] for row in rows],
            )
            == 0
            for table, id_column, rows in [
                ("business_units", "business_unit_id", population.business_units),
                ("regions", "region_id", population.regions),
                ("departments", "department_id", population.departments),
                ("cost_centres", "cost_centre_id", population.cost_centres),
                ("gl_accounts", "gl_account_id", population.gl_accounts),
                ("products", "product_id", population.products),
                ("customers", "customer_id", population.customers),
                ("suppliers", "supplier_id", population.suppliers),
                ("employees", "employee_id", population.employees),
            ]
        )
    finally:
        session.rollback()
        cleanup_population(session, population, generator_version)
        session.close()


def test_repeated_identical_bootstrap_fails_without_duplicate_master_rows() -> None:
    session = SessionLocal()
    generator_version = "m1.3-phase2-repeat-test"
    population = MasterDataGenerator().generate(build_context(generator_version=generator_version))
    original_clock: date | None = None
    original_batch_id: int | None = None
    try:
        assert_postgres_available(session)
        cleanup_population(session, population, generator_version)
        original_clock, original_batch_id = session.execute(
            text(
                """
                SELECT current_simulation_date, current_batch_id
                FROM operations.simulation_control
                WHERE simulation_id = 1
                """
            )
        ).one()
        first_runner = build_master_bootstrap_runner(session)
        first_context = first_runner.build_context(
            simulation_id=1,
            mode=RunMode.BOOTSTRAP,
            generator_version=generator_version,
            target_simulation_date=date(2024, 12, 31),
        )
        first_runner.run(first_context)

        second_runner = build_master_bootstrap_runner(session)
        second_context = second_runner.build_context(
            simulation_id=1,
            mode=RunMode.BOOTSTRAP,
            generator_version=generator_version,
            target_simulation_date=date(2024, 12, 31),
        )

        with pytest.raises(RuntimeError, match="already contains"):
            second_runner.run(second_context)

        counts = {
            "business_units": generated_table_count(session, "business_units", "business_unit_id", [row["business_unit_id"] for row in population.business_units]),
            "regions": generated_table_count(session, "regions", "region_id", [row["region_id"] for row in population.regions]),
            "departments": generated_table_count(session, "departments", "department_id", [row["department_id"] for row in population.departments]),
            "cost_centres": generated_table_count(session, "cost_centres", "cost_centre_id", [row["cost_centre_id"] for row in population.cost_centres]),
            "currencies": int(session.execute(text("SELECT count(*) FROM master.currencies WHERE currency_code = ANY(:values)"), {"values": [row["currency_code"] for row in population.currencies]}).scalar_one()),
            "gl_accounts": generated_table_count(session, "gl_accounts", "gl_account_id", [row["gl_account_id"] for row in population.gl_accounts]),
            "products": generated_table_count(session, "products", "product_id", [row["product_id"] for row in population.products]),
            "customers": generated_table_count(session, "customers", "customer_id", [row["customer_id"] for row in population.customers]),
            "suppliers": generated_table_count(session, "suppliers", "supplier_id", [row["supplier_id"] for row in population.suppliers]),
            "employees": generated_table_count(session, "employees", "employee_id", [row["employee_id"] for row in population.employees]),
        }
        failed_count = session.execute(
            text(
                """
                SELECT count(*)
                FROM operations.ingestion_batches
                WHERE generator_version = :generator_version
                  AND status = 'FAILED'
                """
            ),
            {"generator_version": generator_version},
        ).scalar_one()
        assert counts == EXPECTED_MASTER_COUNTS
        assert failed_count == 1
    finally:
        session.rollback()
        cleanup_population(session, population, generator_version)
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
