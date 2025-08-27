import os
from agents.collector_agent import CollectorAgent
from agents.chart_agent import ChartAgent
from agents.insight_agent import InsightAgent

class IntegratorAgent:
    def __init__(self, db_path="household_finance.db", output_dir="output"):
        self.db_path = db_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def run_demo(self, csv_path: str):
        # Step 1: Collect
        collector = CollectorAgent(self.db_path)
        collector.clear_all()
        collector.load_csv(csv_path)
        collector.close()

        # Step 2: Charts
        chart = ChartAgent(self.db_path, self.output_dir)
        charts = [
            chart.expenses_by_category(),
            chart.income_vs_expense_trend(),
            chart.top_spend_categories_bar(top_n=5)
        ]
        charts = [c for c in charts if c]

        # Step 3: Insights
        insight = InsightAgent(self.db_path)
        insights = insight.generate_insights()

        # Step 4: Report
        report_path = os.path.join(self.output_dir, "report.md")
        with open(report_path, "w") as f:
            f.write("# Household Finance Report (Demo)\n\n")
            f.write("## Insights\n")
            for i in insights:
                f.write(f"- {i}\n")
            f.write("\n## Charts\n")
            for c in charts:
                rel = os.path.basename(c)
                f.write(f"![{rel}]({rel})\n\n")

        return {"charts": charts, "insights": insights, "report": report_path}
