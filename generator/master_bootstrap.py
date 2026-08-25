from sqlalchemy.orm import Session

from generator.context import RunContext
from generator.master_data import MasterDataConfig, MasterDataGenerator
from generator.master_persistence import MasterDataRepository
from generator.repository import SqlAlchemySimulationRepository, SqlAlchemyTransactionManager
from generator.runner import SimulationRunner


def build_master_bootstrap_runner(
    session: Session,
    *,
    config: MasterDataConfig | None = None,
) -> SimulationRunner:
    """Build a Phase 2 bootstrap runner using the approved Phase 1 lifecycle."""

    data_generator = MasterDataGenerator(config)
    master_repository = MasterDataRepository(session)

    def generator_step(context: RunContext) -> int:
        population = data_generator.generate(context)
        return master_repository.bootstrap(context, population)

    simulation_repository = SqlAlchemySimulationRepository(session)
    return SimulationRunner(
        batch_repository=simulation_repository,
        clock_repository=simulation_repository,
        transaction_manager=SqlAlchemyTransactionManager(session),
        generator_step=generator_step,
    )
