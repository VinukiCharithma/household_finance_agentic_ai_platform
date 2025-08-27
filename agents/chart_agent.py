import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

class ChartAgent:
    def __init__(self, db_path="household_finance.db", output_dir="output"):
        self.conn = sqlite3.connect(db_path)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _df(self):
        return pd.read_sql_query("SELECT * FROM records", self.conn, parse_dates=["date"])

    def expenses_by_category(self):
        df = self._df()
        df = df[df["type"].str.lower() == "expense"].copy()
        if df.empty:
            return None
        by_cat = df.groupby("category")["amount"].sum().abs().sort_values(ascending=False)
        plt.figure()
        by_cat.plot(kind="pie", autopct="%1.1f%%")
        plt.title("Expenses by Category")
        plt.ylabel("")
        path = os.path.join(self.output_dir, "expenses_by_category.png")
        plt.savefig(path, bbox_inches="tight")
        plt.close()
        return path

    def income_vs_expense_trend(self):
        df = self._df()
        if df.empty:
            return None
        df["date"] = pd.to_datetime(df["date"])
        daily = df.groupby(["date","type"])["amount"].sum().unstack(fill_value=0)
        daily = daily.sort_index()
        plt.figure()
        daily.plot()
        plt.title("Daily Income vs Expense")
        plt.xlabel("Date")
        plt.ylabel("Amount")
        path = os.path.join(self.output_dir, "income_vs_expense_trend.png")
        plt.savefig(path, bbox_inches="tight")
        plt.close()
        return path

    def top_spend_categories_bar(self, top_n=5):
        df = self._df()
        exp = df[df["type"].str.lower() == "expense"]
        if exp.empty:
            return None
        by_cat = exp.groupby("category")["amount"].sum().abs().sort_values(ascending=False).head(top_n)
        plt.figure()
        by_cat.plot(kind="bar")
        plt.title(f"Top {top_n} Spend Categories")
        plt.xlabel("Category")
        plt.ylabel("Total Spend")
        path = os.path.join(self.output_dir, "top_spend_categories_bar.png")
        plt.savefig(path, bbox_inches="tight")
        plt.close()
        return path
