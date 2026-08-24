from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

from generator.clock import SimulationState
from generator.context import RunContext


class SqlAlchemySimulationRepository:
    """PostgreSQL-backed repository for simulation control and batch metadata."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_simulation_state(self, simulation_id: int) -> SimulationState:
        row = self.session.execute(
            text(
                """
                SELECT simulation_id, current_simulation_date, random_seed
                FROM operations.simulation_control
                WHERE simulation_id = :simulation_id
                """
            ),
            {"simulation_id": simulation_id},
        ).one()
        return SimulationState(
            simulation_id=row.simulation_id,
            current_simulation_date=row.current_simulation_date,
            random_seed=row.random_seed,
        )

    def start_batch(self, context: RunContext) -> int:
        batch_id = self.session.execute(
            text(
                """
                INSERT INTO operations.ingestion_batches (
                    simulation_id,
                    simulation_date,
                    batch_type,
                    status,
                    generator_version
                )
                VALUES (
                    :simulation_id,
                    :simulation_date,
                    :batch_type,
                    'STARTED',
                    :generator_version
                )
                RETURNING batch_id
                """
            ),
            {
                "simulation_id": context.simulation_id,
                "simulation_date": context.simulation_date,
                "batch_type": context.mode.value,
                "generator_version": context.generator_version,
            },
        ).scalar_one()
        self.session.commit()
        return int(batch_id)

    def mark_batch_succeeded(self, batch_id: int, records_generated: int) -> None:
        self.session.execute(
            text(
                """
                UPDATE operations.ingestion_batches
                SET status = 'SUCCEEDED',
                    completed_at = NOW(),
                    records_generated = :records_generated,
                    error_message = NULL
                WHERE batch_id = :batch_id
                """
            ),
            {"batch_id": batch_id, "records_generated": records_generated},
        )
        self.session.commit()

    def mark_batch_failed(self, batch_id: int, error_message: str) -> None:
        self.session.execute(
            text(
                """
                UPDATE operations.ingestion_batches
                SET status = 'FAILED',
                    completed_at = NOW(),
                    error_message = :error_message
                WHERE batch_id = :batch_id
                """
            ),
            {"batch_id": batch_id, "error_message": error_message},
        )
        self.session.commit()

    def advance_clock(self, simulation_id: int, simulation_date: date, batch_id: int) -> None:
        self.session.execute(
            text(
                """
                UPDATE operations.simulation_control
                SET current_simulation_date = :simulation_date,
                    last_run_at = NOW(),
                    current_batch_id = :batch_id,
                    updated_at = NOW()
                WHERE simulation_id = :simulation_id
                """
            ),
            {
                "simulation_id": simulation_id,
                "simulation_date": simulation_date,
                "batch_id": batch_id,
            },
        )
        self.session.commit()


class SqlAlchemyTransactionManager:
    """Transaction manager for generated business records."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def begin(self) -> None:
        self.session.begin()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
