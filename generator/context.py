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

    @classmethod
    def create(
        cls,
        *,
        simulation_id: int,
        mode: str | RunMode,
        simulation_date: date,
        random_seed: int,
        generator_version: str,
        batch_id: int | None = None,
    ) -> "RunContext":
        return cls(
            simulation_id=simulation_id,
            mode=RunMode(mode),
            simulation_date=simulation_date,
            random_seed=random_seed,
            generator_version=generator_version,
            batch_id=batch_id,
        )
