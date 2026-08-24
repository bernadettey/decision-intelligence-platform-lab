from collections.abc import Callable
from dataclasses import replace
from datetime import date
from typing import Protocol

from generator.batch import BatchRepository
from generator.clock import ClockRepository, next_month
from generator.context import RunContext, RunMode


class TransactionManager(Protocol):
    def begin(self) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...


GeneratorStep = Callable[[RunContext], int]


class SimulationRunner:
    """Coordinates batch lifecycle, transaction boundary, and simulation clock updates."""

    def __init__(
        self,
        *,
        batch_repository: BatchRepository,
        clock_repository: ClockRepository,
        transaction_manager: TransactionManager,
        generator_step: GeneratorStep,
    ) -> None:
        self.batch_repository = batch_repository
        self.clock_repository = clock_repository
        self.transaction_manager = transaction_manager
        self.generator_step = generator_step

    def build_context(
        self,
        *,
        simulation_id: int,
        mode: str | RunMode,
        generator_version: str,
        target_simulation_date: date | None = None,
    ) -> RunContext:
        run_mode = RunMode(mode)
        state = self.clock_repository.get_simulation_state(simulation_id)

        if run_mode is RunMode.REPLAY:
            if target_simulation_date is None:
                raise ValueError("REPLAY requires target_simulation_date")
            simulation_date = target_simulation_date
        elif run_mode is RunMode.INCREMENTAL:
            simulation_date = next_month(state.current_simulation_date)
        else:
            simulation_date = target_simulation_date or state.current_simulation_date

        return RunContext(
            simulation_id=simulation_id,
            mode=run_mode,
            simulation_date=simulation_date,
            random_seed=state.random_seed,
            generator_version=generator_version,
        )

    def run(self, context: RunContext) -> int:
        batch_id = self.batch_repository.start_batch(context)
        context_with_batch = replace(context, batch_id=batch_id)

        try:
            self.transaction_manager.begin()
            records_generated = self.generator_step(context_with_batch)
            self.transaction_manager.commit()
        except Exception as exc:
            self.transaction_manager.rollback()
            self.batch_repository.mark_batch_failed(batch_id, str(exc))
            raise

        self.batch_repository.mark_batch_succeeded(batch_id, records_generated)
        if context.mode in (RunMode.BOOTSTRAP, RunMode.INCREMENTAL):
            self.clock_repository.advance_clock(
                context.simulation_id,
                context.simulation_date,
                batch_id,
            )

        return batch_id
