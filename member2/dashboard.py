import streamlit as st

from scoring.model_comparison import compare_models
from reporting.charts import score_comparison_chart, risk_comparison_chart


st.set_page_config(page_title="GuardX — Member 2 Dashboard", layout="wide")
st.title("GuardX — Scoring, Comparison & Regression")

st.info("Starter dashboard. Connect this page to the actual audit results after Member 1's evaluator is integrated.")

sample_runs = [
    {
        "run_id": "demo-ollama-a",
        "model": "model-a",
        "risk_rate": 20.0,
        "security_score": 80.0,
        "results": [
            {"test_id": "T001", "passed": True},
            {"test_id": "T002", "passed": False},
        ],
    },
    {
        "run_id": "demo-ollama-b",
        "model": "model-b",
        "risk_rate": 35.0,
        "security_score": 65.0,
        "results": [
            {"test_id": "T001", "passed": False},
            {"test_id": "T002", "passed": False},
        ],
    },
]

summaries = compare_models(sample_runs)
st.dataframe(summaries, use_container_width=True)

left, right = st.columns(2)

with left:
    chart = score_comparison_chart(summaries)
    if chart:
        st.plotly_chart(chart, use_container_width=True)

with right:
    chart = risk_comparison_chart(summaries)
    if chart:
        st.plotly_chart(chart, use_container_width=True)
