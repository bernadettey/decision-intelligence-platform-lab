from sqlalchemy.orm import Session

from app.repositories.postgres_read_repository import PostgresReadRepository


class QueryService:
    def build_saas_commercial_summary_query(self) -> tuple[str, dict[str, str]]:
        return PostgresReadRepository.SAAS_COMMERCIAL_SUMMARY_SQL, {}

    def run_saas_commercial_summary(self, db: Session) -> tuple[str, list[dict]]:
        sql, _params = self.build_saas_commercial_summary_query()
        rows = PostgresReadRepository(db).fetch_saas_commercial_summary()
        return sql.strip(), rows

    def build_variance_query(self, question: str) -> tuple[str, dict[str, str]]:
        return self.build_saas_commercial_summary_query()

    def run_variance_query(self, db: Session, question: str) -> tuple[str, list[dict]]:
        return self.run_saas_commercial_summary(db)
