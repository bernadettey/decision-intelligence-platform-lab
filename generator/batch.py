from dataclasses import dataclass
from datetime import date
from typing import Protocol

from generator.context import RunContext, RunMode


class BatchRepository(Protocol):
    def start_batch(self, context: RunContext) -> int:
        ...

    def mark_batch_succeeded(self, batch_id: int, records_generated: int) -> None:
        ...

    def mark_batch_failed(self, batch_id: int, error_message: str) -> None:
        ...


@dataclass(frozen=True)
class BatchRecord:
    batch_id: int
    simulation_id: int
    simulation_date: date
    batch_type: RunMode
    generator_version: str
    status: str
    records_generated: int = 0
    error_message: str | None = None
