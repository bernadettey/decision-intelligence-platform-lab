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
                "No matching financial records were found for the requested period. "
                "Please confirm the month, business unit, or metric scope."
            )

        worst = rows[0]
        variance = float(worst["operating_profit_budget_variance"])
        actual_op = float(worst["actual_operating_profit"])
        budget_op = float(worst["budget_operating_profit"])

        direction = "below" if variance < 0 else "above"
        return (
            f"Operating profit was {direction} budget for {worst['business_unit']} in the requested period. "
            f"Actual operating profit was {actual_op:,.0f} versus budget of {budget_op:,.0f}, "
            f"creating a variance of {variance:,.0f}. The primary executive takeaway is that margin delivery "
            f"should be reviewed by business unit, with attention on revenue conversion, COGS pressure, and opex control. "
            f"Metrics used: {', '.join(metrics_used)}."
        )
