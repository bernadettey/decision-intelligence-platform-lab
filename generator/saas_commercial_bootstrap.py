from sqlalchemy.orm import Session

from generator.context import RunContext
from generator.repository import SqlAlchemySimulationRepository, SqlAlchemyTransactionManager
from generator.runner import SimulationRunner
from generator.saas_commercial_data import SaaSCommercialConfig, SaaSCommercialGenerator
from generator.saas_commercial_persistence import SaaSCommercialRepository


def build_saas_commercial_bootstrap_runner(
    session: Session,
    *,
    config: SaaSCommercialConfig | None = None,
) -> SimulationRunner:
    """Build a Phase 3 SaaS operational bootstrap runner."""

    data_generator = SaaSCommercialGenerator(config)
    commercial_repository = SaaSCommercialRepository(session)

    def generator_step(context: RunContext) -> int:
        reference = commercial_repository.load_master_reference()
        population = data_generator.generate(context, reference)
        return commercial_repository.bootstrap(context, population)

    simulation_repository = SqlAlchemySimulationRepository(session)
    return SimulationRunner(
        batch_repository=simulation_repository,
        clock_repository=simulation_repository,
        transaction_manager=SqlAlchemyTransactionManager(session),
        generator_step=generator_step,
    )
