from openai import OpenAI

from app.config import get_settings


class AIService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def generate_commentary(self, question: str, metrics_used: list[str], rows: list[dict]) -> str:
        if self.settings.openai_api_key:
            return self._generate_with_openai(question, metrics_used, rows)
        return self._generate_mock_commentary(question, metrics_used, rows)

    def _generate_with_openai(self, question: str, metrics_used: list[str], rows: list[dict]) -> str:
        client = OpenAI(api_key=self.settings.openai_api_key)
        response = client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an FP&A copilot. Produce concise executive commentary "
                        "for a CFO audience. Focus on drivers, variance, and actions."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Question: {question}\nMetrics: {metrics_used}\nData: {rows}",
                },
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    def _generate_mock_commentary(self, question: str, metrics_used: list[str], rows: list[dict]) -> str:
        if not rows:
            return (
                "No matching V1 PostgreSQL records were found. "
                "Please confirm that the current synthetic data bootstrap has been run."
            )

        top_arr_row = rows[0]
        arr = float(top_arr_row["arr_amount"])
        mrr = float(top_arr_row["mrr_amount"])
        subscriptions = int(top_arr_row["active_subscriptions"])
        events = int(top_arr_row["subscription_events"])
        return (
            f"{top_arr_row['business_unit']} has {subscriptions} active SaaS subscriptions "
            f"in {top_arr_row['region'] or 'unassigned regions'}, representing ARR of {arr:,.0f} "
            f"and MRR of {mrr:,.0f}. The current V1 data layer is reporting from "
            f"schema-qualified SaaS commercial tables, with {events} subscription events "
            f"available for operational traceability. Metrics used: {', '.join(metrics_used)}."
        )
