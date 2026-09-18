import streamlit as st

from app.evaluation.result import EvaluationResult, Violation
from regression.comparison import compare_runs
from reporting.charts import score_comparison_chart, risk_comparison_chart
from scoring.model_comparison import compare_models
from scoring.risk_score import score_evaluation
from storage.results_store import ResultsStore


st.set_page_config(
    page_title="GuardX — Security Audit Dashboard",
    layout="wide",
)

st.title("GuardX — Security Audit Dashboard")
st.caption("Constraint evaluation, risk scoring, model comparison and regression testing")


def make_result(
    test_id: str,
    model: str,
    passed: bool,
    risk_level: str | None = None,
) -> EvaluationResult:
    violations = []

    if risk_level:
        violations.append(
            Violation(
                constraint_id="C1",
                constraint_type="secret_protection",
                risk_level=risk_level,
                description="Synthetic secret protection violation",
                expected="Synthetic secret must remain protected",
                actual="Synthetic secret exposed",
            )
        )

    return EvaluationResult(
        test_id=test_id,
        model=model,
        response="Synthetic demonstration response",
        passed=passed,
        failed=[] if passed else ["C1"],
        violations=violations,
    )


model_a_results = [
    make_result("T001", "model-a", True),
    make_result("T002", "model-a", False, "high"),
    make_result("T003", "model-a", True),
]

model_b_results = [
    make_result("T001", "model-b", True),
    make_result("T002", "model-b", False, "critical"),
    make_result("T003", "model-b", False, "medium"),
]

runs = [
    {
        "run_id": "demo-model-a",
        "model": "model-a",
        "results": model_a_results,
        "average_latency_ms": 120.0,
    },
    {
        "run_id": "demo-model-b",
        "model": "model-b",
        "results": model_b_results,
        "average_latency_ms": 145.0,
    },
]


summaries = compare_models(runs)


st.subheader("Model Comparison")

st.dataframe(
    summaries,
    use_container_width=True,
)


left, right = st.columns(2)

with left:
    st.subheader("Security Score")
    chart = score_comparison_chart(summaries)

    if chart:
        st.plotly_chart(chart, use_container_width=True)

with right:
    st.subheader("Risk Rate")
    chart = risk_comparison_chart(summaries)

    if chart:
        st.plotly_chart(chart, use_container_width=True)


st.subheader("Regression Testing")

baseline_results = [
    make_result("T001", "model-a", False, "high"),
    make_result("T002", "model-a", True),
    make_result("T003", "model-a", False, "medium"),
]

current_results = [
    make_result("T001", "model-a", True),
    make_result("T002", "model-a", True),
    make_result("T003", "model-a", False, "critical"),
]

regression = compare_runs(
    baseline_results,
    current_results,
)

regression_columns = st.columns(4)

regression_columns[0].metric(
    "Fixed",
    len(regression["fixed"]),
)

regression_columns[1].metric(
    "New Failures",
    len(regression["new_failures"]),
)

regression_columns[2].metric(
    "Persistent Failures",
    len(regression["persistent_failures"]),
)

regression_columns[3].metric(
    "Unchanged",
    len(regression["unchanged"]),
)


with st.expander("Regression Details"):
    st.write("Fixed:", regression["fixed"])
    st.write("New failures:", regression["new_failures"])
    st.write("Persistent failures:", regression["persistent_failures"])
    st.write("Unchanged:", regression["unchanged"])


st.subheader("Example Evaluation Details")

selected_result = model_a_results[1]
selected_score = score_evaluation(selected_result)

metric_columns = st.columns(4)

metric_columns[0].metric(
    "Risk Points",
    selected_score.risk_points,
)

metric_columns[1].metric(
    "Risk Rate",
    f"{selected_score.risk_rate:.2f}%",
)

metric_columns[2].metric(
    "Security Score",
    f"{selected_score.security_score:.2f}%",
)

metric_columns[3].metric(
    "Violations",
    selected_score.violation_count,
)


st.subheader("Results Storage")

store = ResultsStore()

if st.button("Save Demo Runs"):
    from datetime import datetime, timezone

    timestamp = datetime.now(timezone.utc).isoformat()

    for summary in summaries:
        store.save_run(
            {
                "run_id": summary["run_id"],
                "model": summary["model"],
                "created_at": timestamp,
                "risk_rate": summary["risk_rate"],
                "security_score": summary["security_score"],
                "results": [],
            }
        )

    st.success("Demo runs saved to SQLite.")

saved_runs = store.list_runs()

if saved_runs:
    st.dataframe(
        saved_runs,
        use_container_width=True,
    )