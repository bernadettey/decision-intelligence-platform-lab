from sqlalchemy import text
from sqlalchemy.orm import Session


class QueryService:
    def build_variance_query(self, question: str) -> tuple[str, dict[str, str]]:
        normalized = question.lower()
        month = "2024-03-01" if "march" in normalized or "mar" in normalized else "2024-01-01"

        sql = """
        SELECT
            a.period,
            bu.name AS business_unit,
            SUM(a.revenue) AS actual_revenue,
            SUM(b.revenue) AS budget_revenue,
            SUM(a.revenue - a.cogs - a.opex) AS actual_operating_profit,
            SUM(b.revenue - b.cogs - b.opex) AS budget_operating_profit,
            SUM(a.revenue - a.cogs - a.opex) - SUM(b.revenue - b.cogs - b.opex) AS operating_profit_budget_variance
        FROM actuals a
        JOIN budgets b
            ON b.period = a.period
            AND b.business_unit_id = a.business_unit_id
            AND b.cost_centre_id = a.cost_centre_id
        JOIN business_units bu ON bu.id = a.business_unit_id
        WHERE a.period = :period
        GROUP BY a.period, bu.name
        ORDER BY operating_profit_budget_variance ASC;
        """
        return sql, {"period": month}

    def run_variance_query(self, db: Session, question: str) -> tuple[str, list[dict]]:
        sql, params = self.build_variance_query(question)
        result = db.execute(text(sql), params)
        rows = [dict(row._mapping) for row in result]
        return sql.strip(), rows
