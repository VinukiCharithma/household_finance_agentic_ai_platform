import sqlite3
import pandas as pd

class InsightAgent:
    def __init__(self, db_path="household_finance.db"):
        self.conn = sqlite3.connect(db_path)

    def _df(self):
        return pd.read_sql_query("SELECT * FROM records", self.conn, parse_dates=["date"])

    def generate_insights(self):
        df = self._df()
        if df.empty:
            return ["No data available. Please load transactions first."]

        insights = []

        income = df[df["type"].str.lower() == "income"]["amount"].sum()
        expense = df[df["type"].str.lower() == "expense"]["amount"].sum()
        net = income + expense
        insights.append(f"Total income: {income:.2f}")
        insights.append(f"Total expenses: {abs(expense):.2f}")
        insights.append(f"Net balance: {net:.2f}")

        exp = df[df["type"].str.lower() == "expense"].copy()
        if not exp.empty:
            by_cat = exp.groupby("category")["amount"].sum().abs().sort_values(ascending=False)
            top_cat = by_cat.index[0]
            top_val = by_cat.iloc[0]
            share = 100.0 * top_val / by_cat.sum() if by_cat.sum() else 0.0
            insights.append(f"Largest expense category: {top_cat} ({top_val:.2f}, {share:.1f}% of expenses)")

        df["month"] = pd.to_datetime(df["date"]).dt.to_period("M")
        monthly = df.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0).sort_index()
        if len(monthly) >= 2:
            last = monthly.iloc[-2]
            cur = monthly.iloc[-1]
            delta = cur.get("expense", 0) - last.get("expense", 0)
            if delta < 0:
                insights.append(f"Expenses decreased by {abs(delta):.2f} compared to previous month.")
            elif delta > 0:
                insights.append(f"Expenses increased by {abs(delta):.2f} compared to previous month.")
            else:
                insights.append("Expenses unchanged vs previous month.")

        recurring = df[df["description"].str.contains("bill|rent|subscription|salary", case=False, na=False)]
        if not recurring.empty:
            approx = recurring.groupby("description")["amount"].mean().abs().sum()
            insights.append(f"Approx recurring (avg by description): {approx:.2f} per month.")

        return insights
