import streamlit as st
if "previous_audit_runs" not in st.session_state:
    st.session_state.previous_audit_runs = None

if "current_audit_runs" not in st.session_state:
    st.session_state.current_audit_runs = None

from app.evaluation.result import EvaluationResult, Violation
from regression.comparison import compare_runs
from reporting.charts import score_comparison_chart, risk_comparison_chart
from scoring.model_comparison import compare_models
from scoring.risk_score import score_evaluation
from storage.results_store import ResultsStore
from datasets.jbb_loader import load_jbb_behaviors


st.set_page_config(
    page_title="GuardX — Security Audit Dashboard",
    layout="wide",
)

st.title("GuardX — Security Audit Dashboard")
st.caption("Constraint evaluation, risk scoring, model comparison and regression testing")

st.subheader("JBB-Behaviors Test Selection")

JBB_DATASET_PATH = "data/datasets/jbb_behaviors/harmful-behaviors.csv"

jbb_test_cases = load_jbb_behaviors(
    JBB_DATASET_PATH,
    limit=None,
    split="harmful",
)

categories = sorted(
    {
        test.constraints[0].metadata.get("category", "Unknown")
        for test in jbb_test_cases
    }
)

selected_category = st.selectbox(
    "Filter prompts by category:",
    options=["All"] + categories,
)

filtered_test_cases = jbb_test_cases

if selected_category != "All":
    filtered_test_cases = [
        test
        for test in jbb_test_cases
        if test.constraints[0].metadata.get("category", "Unknown")
        == selected_category
    ]

selected_test_ids = st.multiselect(
    "Select one or more adversarial prompts to audit:",
    options=[test.test_id for test in filtered_test_cases],
)

if selected_test_ids:
    selected_test_cases = [
        test
        for test in filtered_test_cases
        if test.test_id in selected_test_ids
    ]

    st.write(f"Selected prompts: {len(selected_test_cases)}")

    for test in selected_test_cases:
        st.write(f"**{test.test_id}:** {test.prompt}")
else:
    st.info("Select one or more prompts to begin an audit.")

    st.subheader("Run Selected Audit")

selected_models = st.multiselect(
    "Select model(s) to test:",
    options=[
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
    ],
)

if st.button("Audit Selected Prompts"):
    if not selected_test_ids:
        st.warning("Select at least one JBB prompt.")
    elif not selected_models:
        st.warning("Select at least one model.")
    else:
        from app.models.adapters.groq_adapter import GroqAdapter
        from member2.runner.model_runner import run_model

        audit_runs = []

        for model_name in selected_models:
            st.write(f"Running audit for **{model_name}**...")

            model = GroqAdapter(model_name)

            model_run = run_model(
                model=model,
                test_cases=selected_test_cases,
            )

            audit_runs.append(
                {
                    "model": model_run.model,
                    "results": model_run.results,
                    "run_id": f"interactive-{model_name.replace('/', '-')}",
                    "average_latency_ms": model_run.average_latency_ms,
                }
            )

        audit_summaries = compare_models(audit_runs)

        if st.session_state.previous_audit_runs is None:
           st.session_state.previous_audit_runs = audit_runs
           st.session_state.current_audit_runs = None
        else:
           st.session_state.current_audit_runs = audit_runs

        st.success("Audit completed.")

        st.subheader("Audit Results")

        st.dataframe(
            audit_summaries,
            use_container_width=True,
        )

        st.subheader("Per-Test Results")

        for audit_run in audit_runs:
            st.write(f"### {audit_run['model']}")

            for result in audit_run["results"]:
                score = score_evaluation(result)

                st.write(
                    f"**{result.test_id}** — "
                    f"{'PASS' if result.passed else 'FAIL'}"
                )

                st.write(
                    f"Risk: {score.risk_rate:.2f}% | "
                    f"Security: {score.security_score:.2f}% | "
                    f"Violations: {score.violation_count}"
                )

                if result.violations:
                    with st.expander(
                        f"Violations — {result.test_id}"
                    ):
                        for violation in result.violations:
                            st.write(
                                f"- **{violation.constraint_id}** "
                                f"({violation.risk_level}): "
                                f"{violation.description}"
                            )

        
        st.subheader("Regression Testing")

if (
    st.session_state.previous_audit_runs
    and st.session_state.current_audit_runs
):
    previous_models = {
        run["model"]: run
        for run in st.session_state.previous_audit_runs
    }

    current_models = {
        run["model"]: run
        for run in st.session_state.current_audit_runs
    }

    common_models = sorted(
        set(previous_models) & set(current_models)
    )

    if common_models:
        regression_model = st.selectbox(
            "Select model for regression comparison:",
            options=common_models,
        )

        baseline_run = previous_models[regression_model]
        current_run = current_models[regression_model]

        regression_result = compare_runs(
            baseline_run["results"],
            current_run["results"],
        )

        st.write(
            f"Compared tests: {regression_result['compared_count']}"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Fixed",
            len(regression_result["fixed"]),
        )

        col2.metric(
            "New Failures",
            len(regression_result["new_failures"]),
        )

        col3.metric(
            "Persistent Failures",
            len(regression_result["persistent_failures"]),
        )

        col4.metric(
            "Unchanged",
            len(regression_result["unchanged"]),
        )

        if regression_result["fixed"]:
            st.write(
                "**Fixed:** "
                + ", ".join(regression_result["fixed"])
            )

        if regression_result["new_failures"]:
            st.write(
                "**New Failures:** "
                + ", ".join(regression_result["new_failures"])
            )

        if regression_result["persistent_failures"]:
            st.write(
                "**Persistent Failures:** "
                + ", ".join(
                    regression_result["persistent_failures"]
                )
            )

        if regression_result["unchanged"]:
            st.write(
                "**Unchanged:** "
                + ", ".join(regression_result["unchanged"])
            )
    else:
        st.info(
            "No common models are available for regression comparison."
        )

else:
    st.info(
        "Run an audit twice to compare the current run "
        "against the previous baseline."
    )

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