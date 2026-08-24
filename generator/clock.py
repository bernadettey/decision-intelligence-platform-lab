from dataclasses import dataclass
from datetime import date
from typing import Protocol


class ClockRepository(Protocol):
    def get_simulation_state(self, simulation_id: int) -> "SimulationState":
        ...

    def advance_clock(self, simulation_id: int, simulation_date: date, batch_id: int) -> None:
        ...


@dataclass(frozen=True)
class SimulationState:
    simulation_id: int
    current_simulation_date: date
    random_seed: int


def next_month(simulation_date: date) -> date:
    year = simulation_date.year + (simulation_date.month // 12)
    month = 1 if simulation_date.month == 12 else simulation_date.month + 1
    day = min(simulation_date.day, _days_in_month(year, month))
    return date(year, month, day)


def _days_in_month(year: int, month: int) -> int:
    if month == 12:
        next_month_start = date(year + 1, 1, 1)
    else:
        next_month_start = date(year, month + 1, 1)
    return (next_month_start - date(year, month, 1)).days
