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