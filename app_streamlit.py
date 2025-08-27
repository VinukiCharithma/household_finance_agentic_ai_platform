import streamlit as st
import pandas as pd
import os
from agents.collector_agent import load_or_generate_data, generate_sample_data, CollectorAgent
from agents.integrator_agent import IntegratorAgent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "sample_transactions_50.csv")
DB_PATH = os.path.join(BASE_DIR, "household_finance.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

st.set_page_config(page_title="Agentic Finance Demo", layout="wide")
st.title("💰 Agentic AI Finance Demo (Streamlit)")

# Load (or generate) default dataset on startup
df = load_or_generate_data(DATA_PATH)

st.subheader("📂 Transactions")
st.dataframe(df, use_container_width=True)

# Allow user to upload another CSV and replace the dataset
st.subheader("Upload CSV (optional)")
uploaded_file = st.file_uploader("Upload transactions CSV", type=["csv"])

if uploaded_file:
    # Save uploaded to DATA_PATH so integrator/collector use same file path
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())
    df = pd.read_csv(DATA_PATH)
    st.success("Uploaded file saved and loaded.")
    st.dataframe(df.head())

st.subheader("Summary")
total_income = df[df['type'] == 'income']['amount'].sum()
total_expense = df[df['type'] == 'expense']['amount'].sum()
balance = total_income + total_expense

col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"${total_income:,.2f}")
col2.metric("Total Expenses", f"${abs(total_expense):,.2f}")
col3.metric("Balance", f"${balance:,.2f}")

# Run the full pipeline
if st.button("🚀 Run Full Agent Pipeline"):
    integrator = IntegratorAgent(DB_PATH, OUTPUT_DIR)
    result = integrator.run_demo(DATA_PATH)

    st.subheader("🧠 Insights")
    for insight in result["insights"]:
        st.write(f"- {insight}")

    st.subheader("📊 Charts")
    for chart_path in result["charts"]:
        st.image(chart_path, use_column_width=True)

    st.subheader("📑 Report")
    with open(result["report"], "r") as f:
        st.markdown(f.read())

st.info("Tip: You can upload your own CSV (must include date,category,description,amount,type).")
