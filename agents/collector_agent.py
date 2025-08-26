import os
import sqlite3
import pandas as pd

class CollectorAgent:
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

    def close(self):
        self.conn.close()