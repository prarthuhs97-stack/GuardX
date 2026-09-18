import sys
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

# -------------------------------------------------------------------
# Project import paths
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MEMBER2_ROOT = PROJECT_ROOT / "member2"

for path in (PROJECT_ROOT, MEMBER2_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

# -------------------------------------------------------------------
# Project imports
# -------------------------------------------------------------------

from app.models.adapters.groq_adapter import GroqAdapter
from datasets.jbb_loader import load_jbb_behaviors
from regression.comparison import compare_runs
from runner.model_runner import run_model
from scoring.model_comparison import compare_models
from scoring.risk_score import score_evaluation
from storage.results_store import ResultsStore


# -------------------------------------------------------------------
# Page configuration
# -------------------------------------------------------------------

st.set_page_config(
    page_title="GuardX — LLM Security Audit",
    page_icon="🛡️",
    layout="wide",
)

st.title("GuardX — LLM Security Audit")

st.caption(
    "Adversarial LLM testing with risk scoring, model comparison, "
    "regression testing, and persistent audit history."
)


# -------------------------------------------------------------------
# Session state
# -------------------------------------------------------------------

if "previous_audit_runs" not in st.session_state:
    st.session_state.previous_audit_runs = None

if "current_audit_runs" not in st.session_state:
    st.session_state.current_audit_runs = None


# -------------------------------------------------------------------
# Dataset
# -------------------------------------------------------------------

JBB_DATASET_PATH = (
    PROJECT_ROOT
    / "data"
    / "datasets"
    / "jbb_behaviors"
    / "harmful-behaviors.csv"
)

try:
    jbb_test_cases = load_jbb_behaviors(
        JBB_DATASET_PATH,
        limit=None,
        split="harmful",
    )
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()


# -------------------------------------------------------------------
# Audit configuration
# -------------------------------------------------------------------

st.subheader("Audit Configuration")

audit_mode = st.radio(
    "Choose audit mode:",
    options=[
        "Single Prompt",
        "Category Batch",
        "Full Dataset",
    ],
    horizontal=True,
)


# -------------------------------------------------------------------
# Select prompts according to audit mode
# -------------------------------------------------------------------

selected_test_cases = []


if audit_mode == "Single Prompt":

    st.write("Select one adversarial prompt to test.")

    categories = sorted(
        {
            test.constraints[0].metadata.get(
                "category",
                "Unknown",
            )
            for test in jbb_test_cases
        }
    )

    selected_category = st.selectbox(
        "Filter by category:",
        options=["All"] + categories,
    )

    if selected_category == "All":
        filtered_test_cases = jbb_test_cases
    else:
        filtered_test_cases = [
            test
            for test in jbb_test_cases
            if test.constraints[0].metadata.get(
                "category",
                "Unknown",
            )
            == selected_category
        ]

    selected_test_id = st.selectbox(
        "Select adversarial prompt:",
        options=[
            test.test_id
            for test in filtered_test_cases
        ],
    )

    selected_test_cases = [
        test
        for test in filtered_test_cases
        if test.test_id == selected_test_id
    ]

elif audit_mode == "Category Batch":

    st.write(
        "Run multiple adversarial prompts from one JBB category."
    )

    categories = sorted(
        {
            test.constraints[0].metadata.get(
                "category",
                "Unknown",
            )
            for test in jbb_test_cases
        }
    )

    selected_category = st.selectbox(
        "Select category:",
        options=categories,
    )

    category_cases = [
        test
        for test in jbb_test_cases
        if test.constraints[0].metadata.get(
            "category",
            "Unknown",
        )
        == selected_category
    ]

    batch_size = st.slider(
        "Number of prompts:",
        min_value=1,
        max_value=len(category_cases),
        value=min(5, len(category_cases)),
    )

    selected_test_cases = category_cases[:batch_size]

    st.write(
        f"Selected {len(selected_test_cases)} "
        f"prompts from `{selected_category}`."
    )

else:

    st.write(
        "Run the complete JBB harmful-behaviors dataset."
    )

    batch_size = st.slider(
        "Number of prompts:",
        min_value=1,
        max_value=len(jbb_test_cases),
        value=min(10, len(jbb_test_cases)),
        help=(
            "Increase this to 100 to run the complete "
            "harmful-behaviors dataset."
        ),
    )

    selected_test_cases = jbb_test_cases[:batch_size]

    st.write(
        f"Selected {len(selected_test_cases)} "
        f"of {len(jbb_test_cases)} available prompts."
    )


# -------------------------------------------------------------------
# Show selected prompts
# -------------------------------------------------------------------

if selected_test_cases:

    with st.expander(
        f"View selected prompts ({len(selected_test_cases)})"
    ):
        for test in selected_test_cases:

            category = test.constraints[0].metadata.get(
                "category",
                "Unknown",
            )

            st.write(
                f"**{test.test_id}** — `{category}`"
            )

            st.caption(test.prompt)

else:

    st.warning(
        "No prompts are currently selected."
    )


# -------------------------------------------------------------------
# Model selection
# -------------------------------------------------------------------

st.subheader("Model Selection")

selected_models = st.multiselect(
    "Select model(s) to test:",
    options=[
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
    ],
)


# -------------------------------------------------------------------
# Run audit
# -------------------------------------------------------------------

st.subheader("Run Audit")

if st.button(
    "Start Audit",
    type="primary",
):

    if not selected_test_cases:
        st.warning(
            "Select at least one prompt."
        )
        st.stop()

    if not selected_models:
        st.warning(
            "Select at least one model."
        )
        st.stop()

    audit_runs = []

    progress = st.progress(
        0,
        text="Starting audit...",
    )

    total_models = len(selected_models)

    for model_index, model_name in enumerate(
        selected_models,
        start=1,
    ):

        st.write(
            f"Running audit for **{model_name}**..."
        )

        try:

            model = GroqAdapter(model_name)

            model_run = run_model(
                model=model,
                test_cases=selected_test_cases,
            )

        except Exception as exc:

            st.error(
                f"Audit failed for {model_name}: {exc}"
            )
            continue

        timestamp = datetime.now(
            timezone.utc
        ).strftime(
            "%Y%m%d%H%M%S%f"
        )

        audit_runs.append(
            {
                "model": model_run.model,
                "results": model_run.results,
                "run_id": (
                    "interactive-"
                    f"{model_name.replace('/', '-')}-"
                    f"{timestamp}"
                ),
                "average_latency_ms": (
                    model_run.average_latency_ms
                ),
            }
        )

        progress.progress(
            model_index / total_models,
            text=(
                f"Completed {model_name}"
            ),
        )

    if not audit_runs:

        st.error(
            "No audit runs completed."
        )
        st.stop()

    # ---------------------------------------------------------------
    # Model summaries
    # ---------------------------------------------------------------

    audit_summaries = compare_models(
        audit_runs
    )

    # ---------------------------------------------------------------
    # Regression state
    # ---------------------------------------------------------------

    if st.session_state.previous_audit_runs is None:

        st.session_state.previous_audit_runs = (
            audit_runs
        )

        st.session_state.current_audit_runs = None

        is_baseline_run = True

    else:

        st.session_state.current_audit_runs = (
            audit_runs
        )

        is_baseline_run = False

    # ---------------------------------------------------------------
    # Persistent storage
    # ---------------------------------------------------------------

    results_store = ResultsStore()

    for audit_run in audit_runs:

        summary = next(
            item
            for item in audit_summaries
            if item["model"]
            == audit_run["model"]
        )

        results_store.save_evaluation_results(
            run_id=audit_run["run_id"],
            model=audit_run["model"],
            created_at=datetime.now(
                timezone.utc
            ).isoformat(),
            results=audit_run["results"],
            risk_rate=summary["risk_rate"],
            security_score=summary[
                "security_score"
            ],
        )

    if is_baseline_run:

        st.success(
            "Audit completed and saved as "
            "the regression baseline."
        )

    else:

        st.success(
            "Audit completed and saved as "
            "the current regression run."
        )


# -------------------------------------------------------------------
# Determine displayed audit
# -------------------------------------------------------------------

if st.session_state.current_audit_runs is not None:

    displayed_runs = (
        st.session_state.current_audit_runs
    )

elif st.session_state.previous_audit_runs is not None:

    displayed_runs = (
        st.session_state.previous_audit_runs
    )

else:

    displayed_runs = None


# -------------------------------------------------------------------
# Audit results
# -------------------------------------------------------------------

if displayed_runs:

    st.subheader("Audit Results")

    displayed_summaries = compare_models(
        displayed_runs
    )

    st.dataframe(
        displayed_summaries,
        use_container_width=True,
    )


    # ---------------------------------------------------------------
    # Per-test results
    # ---------------------------------------------------------------

    st.subheader("Per-Test Results")

    for audit_run in displayed_runs:

        st.write(
            f"### {audit_run['model']}"
        )

        for result in audit_run["results"]:

            score = score_evaluation(
                result
            )

            status = (
                "PASS"
                if result.passed
                else "FAIL"
            )

            st.write(
                f"**{result.test_id}** — {status}"
            )

            st.write(
                f"Risk: {score.risk_rate:.2f}% | "
                f"Security: "
                f"{score.security_score:.2f}% | "
                f"Violations: "
                f"{score.violation_count}"
            )

            if result.violations:

                with st.expander(
                    f"Violations — "
                    f"{result.test_id}"
                ):

                    for violation in (
                        result.violations
                    ):

                        st.write(
                            f"- **"
                            f"{violation.constraint_id}"
                            f"** "
                            f"({violation.risk_level}): "
                            f"{violation.description}"
                        )


# -------------------------------------------------------------------
# Regression testing
# -------------------------------------------------------------------

st.subheader("Regression Testing")

if (
    st.session_state.previous_audit_runs
    and st.session_state.current_audit_runs
):

    previous_models = {
        run["model"]: run
        for run in (
            st.session_state
            .previous_audit_runs
        )
    }

    current_models = {
        run["model"]: run
        for run in (
            st.session_state
            .current_audit_runs
        )
    }

    common_models = sorted(
        set(previous_models)
        & set(current_models)
    )

    if common_models:

        regression_model = st.selectbox(
            "Select model for regression comparison:",
            options=common_models,
        )

        baseline_run = (
            previous_models[
                regression_model
            ]
        )

        current_run = (
            current_models[
                regression_model
            ]
        )

        regression_result = compare_runs(
            baseline_run["results"],
            current_run["results"],
        )

        st.write(
            "Compared tests: "
            f"{regression_result['compared_count']}"
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )

        col1.metric(
            "Fixed",
            len(
                regression_result["fixed"]
            ),
        )

        col2.metric(
            "New Failures",
            len(
                regression_result[
                    "new_failures"
                ]
            ),
        )

        col3.metric(
            "Persistent Failures",
            len(
                regression_result[
                    "persistent_failures"
                ]
            ),
        )

        col4.metric(
            "Unchanged",
            len(
                regression_result[
                    "unchanged"
                ]
            ),
        )

        if regression_result["fixed"]:

            st.write(
                "**Fixed:** "
                + ", ".join(
                    regression_result[
                        "fixed"
                    ]
                )
            )

        if regression_result[
            "new_failures"
        ]:

            st.write(
                "**New Failures:** "
                + ", ".join(
                    regression_result[
                        "new_failures"
                    ]
                )
            )

        if regression_result[
            "persistent_failures"
        ]:

            st.write(
                "**Persistent Failures:** "
                + ", ".join(
                    regression_result[
                        "persistent_failures"
                    ]
                )
            )

        if regression_result[
            "unchanged"
        ]:

            st.write(
                "**Unchanged:** "
                + ", ".join(
                    regression_result[
                        "unchanged"
                    ]
                )
            )

else:

    st.info(
        "Run an audit twice with the same "
        "model and prompt set to perform "
        "regression comparison."
    )


# -------------------------------------------------------------------
# Audit history
# -------------------------------------------------------------------

st.subheader("Audit History")

history_store = ResultsStore()

stored_runs = (
    history_store.list_runs()
)

if stored_runs:

    history_rows = []

    for run in stored_runs:

        history_rows.append(
            {
                "Run ID": run["run_id"],
                "Model": run["model"],
                "Created At": run[
                    "created_at"
                ],
                "Risk Rate": run.get(
                    "risk_rate"
                ),
                "Security Score": run.get(
                    "security_score"
                ),
                "Tests": len(
                    run.get(
                        "results",
                        [],
                    )
                ),
            }
        )

    st.dataframe(
        history_rows,
        use_container_width=True,
    )

else:

    st.info(
        "No stored audit runs yet."
    )