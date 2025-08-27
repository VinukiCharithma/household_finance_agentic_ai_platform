import os
import sqlite3
import pandas as pd
import random
import datetime

DATA_PATH_DEFAULT = "data/sample_transactions_50.csv"

def generate_sample_data(path=DATA_PATH_DEFAULT, n=50):
    categories = {
        "income": ["Salary", "Freelance", "Investment", "Gift"],
        "expense": ["Groceries", "Utilities", "Rent", "Dining", "Transport", "Entertainment", "Subscriptions"]
    }

    records = []
    start_date = datetime.date(2025, 1, 1)

    for _ in range(n):
        date = start_date + datetime.timedelta(days=random.randint(0, 60))
        if random.random() < 0.3:  # 30% income
            cat_choice = random.choice(categories["income"])
            amount = random.randint(200, 3000)
            record_type = "income"
        else:
            cat_choice = random.choice(categories["expense"])
            amount = -random.randint(10, 800)
            record_type = "expense"

        records.append({
            "date": date.isoformat(),
            "category": cat_choice,
            "description": f"{cat_choice} payment",
            "amount": amount,
            "type": record_type
        })

    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    return df

def load_or_generate_data(path=DATA_PATH_DEFAULT):
    """Return a DataFrame loaded from path, or generate & save a sample if missing."""
    if os.path.exists(path):
        return pd.read_csv(path)
    else:
        return generate_sample_data(path)

class CollectorAgent:
    """
    CollectorAgent: loads transactions from CSV and stores them in SQLite.
    Methods:
      - load_csv(csv_source) : csv_source can be filepath or file-like object
      - clear_all()
      - close()
    """
    def __init__(self, db_path="household_finance.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._ensure_schema()

    def _ensure_schema(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            description TEXT,
            amount REAL,
            type TEXT
        );
        """)
        self.conn.commit()

    def load_csv(self, csv_source):
        """
        Load CSV rows into DB. csv_source may be a filepath (str) or file-like object.
        Dates will be normalized to YYYY-MM-DD.
        """
        df = pd.read_csv(csv_source)
        if "date" not in df.columns:
            raise ValueError("CSV must contain a 'date' column")
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        # Ensure the expected columns exist
        expected = {"date", "category", "description", "amount", "type"}
        if not expected.issubset(set(df.columns)):
            missing = expected - set(df.columns)
            raise ValueError(f"CSV missing required columns: {missing}")
        df.to_sql("records", self.conn, if_exists="append", index=False)

    def clear_all(self):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM records;")
        self.conn.commit()

    def close(self):
        self.conn.close()
