from dataclasses import dataclass, field
from datetime import date

import pytest
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal
from generator.batch import BatchRecord
from generator.clock import SimulationState
from generator.context import RunContext, RunMode
from generator.ids import deterministic_id
from generator.repository import SqlAlchemySimulationRepository, SqlAlchemyTransactionManager
from generator.runner import SimulationRunner


@dataclass
class FakeSimulationRepository:
    current_simulation_date: date = date(2024, 2, 29)
    random_seed: int = 424242
    batches: dict[int, BatchRecord] = field(default_factory=dict)
    current_batch_id: int | None = None
    next_batch_id: int = 1
    fail_clock_advance: bool = False

    def get_simulation_state(self, simulation_id: int) -> SimulationState:
        return SimulationState(
            simulation_id=simulation_id,
            current_simulation_date=self.current_simulation_date,
            random_seed=self.random_seed,
        )

    def start_batch(self, context: RunContext) -> int:
        batch_id = self.next_batch_id
        self.next_batch_id += 1
        self.batches[batch_id] = BatchRecord(
            batch_id=batch_id,
            simulation_id=context.simulation_id,
            simulation_date=context.simulation_date,
            batch_type=context.mode,
            generator_version=context.generator_version,
            status="STARTED",
        )
        return batch_id

    def mark_batch_succeeded(self, batch_id: int, records_generated: int) -> None:
        batch = self.batches[batch_id]
        self.batches[batch_id] = BatchRecord(
            **{**batch.__dict__, "status": "SUCCEEDED", "records_generated": records_generated}
        )

    def mark_batch_failed(self, batch_id: int, error_message: str) -> None:
        batch = self.batches[batch_id]
        self.batches[batch_id] = BatchRecord(
            **{**batch.__dict__, "status": "FAILED", "error_message": error_message}
        )

    def advance_clock(self, simulation_id: int, simulation_date: date, batch_id: int) -> None:
        if self.fail_clock_advance:
            raise RuntimeError("clock advance failed")
        self.current_simulation_date = simulation_date
        self.current_batch_id = batch_id


@dataclass
class FakeTransactionManager:
    staged_records: list[str] = field(default_factory=list)
    committed_records: list[str] = field(default_factory=list)
    began: bool = False
    committed: bool = False
    rolled_back: bool = False

    def begin(self) -> None:
        self.began = True

    def commit(self) -> None:
        self.committed = True
        self.committed_records.extend(self.staged_records)
        self.staged_records.clear()

    def rollback(self) -> None:
        self.rolled_back = True
        self.staged_records.clear()


def build_runner(
    repository: FakeSimulationRepository,
    transaction_manager: FakeTransactionManager,
    *,
    fail: bool = False,
) -> SimulationRunner:
    def generator_step(context: RunContext) -> int:
        transaction_manager.staged_records.append(
            deterministic_id(
                context.simulation_date,
                context.random_seed,
                context.generator_version,
                "placeholder",
                prefix="event",
            )
        )
        if fail:
            raise RuntimeError("synthetic generation failed")
        return 1

    return SimulationRunner(
        batch_repository=repository,
        clock_repository=repository,
        transaction_manager=transaction_manager,
        generator_step=generator_step,
    )


def test_deterministic_id_uses_logical_inputs() -> None:
    first = deterministic_id("2024-03-31", 424242, "v1", "customer-1", prefix="evt")
    second = deterministic_id("2024-03-31", 424242, "v1", "customer-1", prefix="evt")
    changed_version = deterministic_id("2024-03-31", 424242, "v2", "customer-1", prefix="evt")

    assert first == second
    assert first.startswith("evt_")
    assert first != changed_version


def test_deterministic_id_uses_unambiguous_serialization() -> None:
    first = deterministic_id("a|b", "c")
    second = deterministic_id("a", "b|c")

    assert first != second


def test_invalid_run_mode_is_rejected() -> None:
    repository = FakeSimulationRepository()
    transaction_manager = FakeTransactionManager()
    runner = build_runner(repository, transaction_manager)

    with pytest.raises(ValueError):
        runner.build_context(
            simulation_id=1,
            mode="BAD_MODE",
            generator_version="m1.3-phase1",
        )


def test_incremental_advances_clock_after_success() -> None:
    repository = FakeSimulationRepository()
    transaction_manager = FakeTransactionManager()
    runner = build_runner(repository, transaction_manager)
    context = runner.build_context(
        simulation_id=1,
        mode=RunMode.INCREMENTAL,
        generator_version="m1.3-phase1",
    )

    batch_id = runner.run(context)

    assert context.simulation_date == date(2024, 3, 29)
    assert repository.current_simulation_date == date(2024, 3, 29)
    assert repository.current_batch_id == batch_id
    assert repository.batches[batch_id].status == "SUCCEEDED"
    assert transaction_manager.committed_records


def test_bootstrap_advances_clock_after_success() -> None:
    repository = FakeSimulationRepository()
    transaction_manager = FakeTransactionManager()
    runner = build_runner(repository, transaction_manager)
    context = runner.build_context(
        simulation_id=1,
        mode=RunMode.BOOTSTRAP,
        generator_version="m1.3-phase1",
        target_simulation_date=date(2024, 12, 31),
    )

    batch_id = runner.run(context)

    assert repository.current_simulation_date == date(2024, 12, 31)
    assert repository.current_batch_id == batch_id
    assert repository.batches[batch_id].status == "SUCCEEDED"


def test_replay_does_not_advance_clock() -> None:
    repository = FakeSimulationRepository()
    transaction_manager = FakeTransactionManager()
    runner = build_runner(repository, transaction_manager)
    context = runner.build_context(
        simulation_id=1,
        mode=RunMode.REPLAY,
        generator_version="m1.3-phase1",
        target_simulation_date=date(2024, 1, 31),
    )

    batch_id = runner.run(context)

    assert repository.current_simulation_date == date(2024, 2, 29)
    assert repository.current_batch_id is None
    assert repository.batches[batch_id].batch_type is RunMode.REPLAY
    assert repository.batches[batch_id].status == "SUCCEEDED"


def test_clock_advance_failure_rolls_back_success_and_marks_failed() -> None:
    repository = FakeSimulationRepository(fail_clock_advance=True)
    transaction_manager = FakeTransactionManager()
    runner = build_runner(repository, transaction_manager)
    context = runner.build_context(
        simulation_id=1,
        mode=RunMode.INCREMENTAL,
        generator_version="m1.3-phase1",
    )

    with pytest.raises(RuntimeError, match="clock advance failed"):
        runner.run(context)

    failed_batch = repository.batches[1]
    assert transaction_manager.rolled_back is True
    assert transaction_manager.committed is False
    assert transaction_manager.committed_records == []
    assert failed_batch.status == "FAILED"
    assert failed_batch.error_message == "RuntimeError: clock advance failed"
    assert repository.current_simulation_date == date(2024, 2, 29)
    assert repository.current_batch_id is None


def test_failure_rolls_back_business_records_and_persists_failed_batch() -> None:
    repository = FakeSimulationRepository()
    transaction_manager = FakeTransactionManager()
    runner = build_runner(repository, transaction_manager, fail=True)
    context = runner.build_context(
        simulation_id=1,
        mode=RunMode.INCREMENTAL,
        generator_version="m1.3-phase1",
    )

    with pytest.raises(RuntimeError, match="synthetic generation failed"):
        runner.run(context)

    failed_batch = repository.batches[1]
    assert transaction_manager.rolled_back is True
    assert transaction_manager.committed_records == []
    assert transaction_manager.staged_records == []
    assert failed_batch.status == "FAILED"
    assert failed_batch.error_message == "RuntimeError: synthetic generation failed"
    assert repository.current_simulation_date == date(2024, 2, 29)


def test_sqlalchemy_failure_persists_failed_batch_and_rolls_back_business_records() -> None:
    session = SessionLocal()
    batch_id: int | None = None
    initial_clock: date | None = None
    marker = deterministic_id("integration-failure", prefix="business_event")

    try:
        try:
            session.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            pytest.skip(f"PostgreSQL test database is unavailable: {exc}")

        initial_clock = session.execute(
            text(
                """
                SELECT current_simulation_date
                FROM operations.simulation_control
                WHERE simulation_id = 1
                """
            )
        ).scalar_one()
        session.rollback()

        repository = SqlAlchemySimulationRepository(session)
        transaction_manager = SqlAlchemyTransactionManager(session)

        def failing_generator_step(context: RunContext) -> int:
            session.execute(
                text(
                    """
                    INSERT INTO operations.business_events (
                        event_date,
                        event_type,
                        event_description,
                        severity,
                        ingestion_batch_id
                    )
                    VALUES (
                        :event_date,
                        'integration_failure_probe',
                        :event_description,
                        'LOW',
                        :batch_id
                    )
                    """
                ),
                {
                    "event_date": context.simulation_date,
                    "event_description": marker,
                    "batch_id": context.batch_id,
                },
            )
            raise RuntimeError("integration generation failed")

        runner = SimulationRunner(
            batch_repository=repository,
            clock_repository=repository,
            transaction_manager=transaction_manager,
            generator_step=failing_generator_step,
        )
        context = runner.build_context(
            simulation_id=1,
            mode=RunMode.INCREMENTAL,
            generator_version="m1.3-phase1-test",
        )

        with pytest.raises(RuntimeError, match="integration generation failed"):
            runner.run(context)

        batch_id = session.execute(
            text(
                """
                SELECT max(batch_id)
                FROM operations.ingestion_batches
                WHERE generator_version = 'm1.3-phase1-test'
                """
            )
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
        business_rows = session.execute(
            text(
                """
                SELECT count(*)
                FROM operations.business_events
                WHERE event_description = :marker
                """
            ),
            {"marker": marker},
        ).scalar_one()
        current_clock = session.execute(
            text(
                """
                SELECT current_simulation_date
                FROM operations.simulation_control
                WHERE simulation_id = 1
                """
            )
        ).scalar_one()

        assert batch.status == "FAILED"
        assert batch.error_message == "RuntimeError: integration generation failed"
        assert business_rows == 0
        assert current_clock == initial_clock
    finally:
        session.rollback()
        if batch_id is not None:
            session.execute(
                text("DELETE FROM operations.ingestion_batches WHERE batch_id = :batch_id"),
                {"batch_id": batch_id},
            )
            session.commit()
        session.close()
