from sqlalchemy import text
from sqlalchemy.orm import Session


class PostgresReadRepository:
    """Read-only backend queries over the current V1 PostgreSQL schema."""

    SAAS_COMMERCIAL_SUMMARY_SQL = """
    WITH subscription_event_summary AS (
        SELECT
            subscription_id,
            COUNT(*) AS subscription_events,
            SUM(arr_delta) AS arr_event_delta
        FROM operations.subscription_events
        GROUP BY subscription_id
    )
    SELECT
        bu.business_unit_name AS business_unit,
        r.region_name AS region,
        COUNT(DISTINCT cc.contract_id) AS active_contracts,
        COUNT(DISTINCT s.subscription_id) AS active_subscriptions,
        COALESCE(SUM(ses.subscription_events), 0) AS subscription_events,
        COALESCE(SUM(s.arr_amount), 0) AS arr_amount,
        COALESCE(SUM(s.mrr_amount), 0) AS mrr_amount,
        COALESCE(SUM(ses.arr_event_delta), 0) AS arr_event_delta
    FROM operations.subscriptions s
    JOIN operations.customer_contracts cc
        ON cc.contract_id = s.contract_id
    JOIN master.business_units bu
        ON bu.business_unit_id = s.business_unit_id
    LEFT JOIN master.regions r
        ON r.region_id = s.region_id
    LEFT JOIN subscription_event_summary ses
        ON ses.subscription_id = s.subscription_id
    WHERE cc.contract_type = 'SAAS'
      AND cc.contract_status = 'ACTIVE'
      AND s.subscription_status = 'ACTIVE'
      AND s.is_deleted = false
      AND cc.is_deleted = false
    GROUP BY bu.business_unit_name, r.region_name
    ORDER BY arr_amount DESC, bu.business_unit_name, r.region_name;
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def fetch_saas_commercial_summary(self) -> list[dict]:
        result = self.db.execute(text(self.SAAS_COMMERCIAL_SUMMARY_SQL))
        return [dict(row._mapping) for row in result]
