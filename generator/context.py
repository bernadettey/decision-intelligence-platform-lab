from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class RunMode(StrEnum):
    BOOTSTRAP = "BOOTSTRAP"
    INCREMENTAL = "INCREMENTAL"
    REPLAY = "REPLAY"


@dataclass(frozen=True)
class RunContext:
    """Immutable inputs for one synthetic simulation run."""

    simulation_id: int
    mode: RunMode
    simulation_date: date
    random_seed: int
    generator_version: str
    batch_id: int | None = None
