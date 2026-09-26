import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import os

# -------------------------------------------------------------------
# Project paths
# -------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MEMBER2_ROOT = PROJECT_ROOT / "member2"

# -------------------------------------------------------------------
# Project import paths
# -------------------------------------------------------------------

for path in (PROJECT_ROOT, MEMBER2_ROOT):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

# -------------------------------------------------------------------
# Environment
# -------------------------------------------------------------------

ENV_FILE = PROJECT_ROOT / ".env"

from dotenv import load_dotenv

load_dotenv(dotenv_path=ENV_FILE)

# -------------------------------------------------------------------
# Third-party imports
# -------------------------------------------------------------------

import streamlit as st

# -------------------------------------------------------------------
# Project imports
# -------------------------------------------------------------------

from app.constraints.constraint import Constraint, RiskLevel
from app.models.adapters.groq_adapter import GroqAdapter
from app.models.adapters.ollama_adapter import OllamaAdapter

from datasets.jbb_loader import load_jbb_behaviors
from regression.comparison import compare_runs
from runner.audit_runner import AuditTestCase
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
    "regression testing, custom prompts, and persistent audit history."
)


# -------------------------------------------------------------------
# Session state
# -------------------------------------------------------------------

if "previous_audit_runs" not in st.session_state:
    st.session_state.previous_audit_runs = None

if "current_audit_runs" not in st.session_state:
    st.session_state.current_audit_runs = None

if "current_response_records" not in st.session_state:
    st.session_state.current_response_records = {}

if "previous_response_records" not in st.session_state:
    st.session_state.previous_response_records = {}

if "audit_source" not in st.session_state:
    st.session_state.audit_source = None


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
        "Custom Prompt",
    ],
    horizontal=True,
)


# -------------------------------------------------------------------
# Prompt selection
# -------------------------------------------------------------------

selected_test_cases = []
custom_prompt = ""
custom_constraint_description = ""

is_custom_audit = audit_mode == "Custom Prompt"


if audit_mode == "Single Prompt":

    st.write(
        "Select one adversarial prompt to test."
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
        "Run multiple adversarial prompts "
        "from one JBB category."
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


elif audit_mode == "Full Dataset":

    st.write(
        "Run the JBB harmful-behaviors dataset."
    )

    batch_size = st.slider(
        "Number of prompts:",
        min_value=1,
        max_value=len(jbb_test_cases),
        value=min(10, len(jbb_test_cases)),
        help=(
            "Set this to 100 to run the "
            "complete JBB dataset."
        ),
    )

    selected_test_cases = jbb_test_cases[:batch_size]

    st.write(
        f"Selected {len(selected_test_cases)} "
        f"of {len(jbb_test_cases)} available prompts."
    )


else:
    # ---------------------------------------------------------------
    # Custom Prompt
    # ---------------------------------------------------------------

    st.write(
        "Test your own prompt against a selected model "
        "using GuardX's existing evaluation and risk-scoring pipeline."
    )

    custom_prompt = st.text_area(
        "Enter your prompt:",
        height=180,
        placeholder=(
            "Example: Explain how you would handle a request "
            "that asks you to reveal a protected synthetic secret."
        ),
    )

    st.write("### Constraint")

    custom_constraint_description = st.text_area(
        "What should the model be required to follow?",
        height=120,
        placeholder=(
            "Example: Do not reveal protected or secret information."
        ),
        help=(
            "This describes the semantic constraint that GuardX "
            "will evaluate against the model response."
        ),
    )

    st.info(
    "GuardX will convert your constraint into a runtime semantic "
    "constraint and evaluate the model response using the existing "
    "GuardX Evaluator and risk-scoring pipeline."
)

    

    if custom_prompt.strip():
        st.subheader("Custom Prompt Preview")
        st.code(custom_prompt.strip(), language="text")


# -------------------------------------------------------------------
# Selected prompt preview
# -------------------------------------------------------------------

if selected_test_cases and not is_custom_audit:

    with st.expander(
        f"View selected prompts ({len(selected_test_cases)})"
    ):

        for test in selected_test_cases:

            category = (
                test.constraints[0]
                .metadata
                .get(
                    "category",
                    "Unknown",
                )
            )

            st.write(
                f"**{test.test_id}** — "
                f"`{category}`"
            )

            st.caption(test.prompt)

elif not is_custom_audit and not selected_test_cases:

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
        "qwen2.5:0.5b",
        "gemma3:1b",
    ],
    help=(
        "Groq models run through the Groq API. "
        "Qwen and Gemma run locally through Ollama."
    ),
)


# -------------------------------------------------------------------
# Audit execution
# -------------------------------------------------------------------

st.subheader("Run Audit")

if st.button(
    "Start Audit",
    type="primary",
    key="start_audit_button",
):

    if is_custom_audit:

        if not custom_prompt.strip():
            st.warning(
                "Enter a custom prompt before starting the audit."
            )
            st.stop()

        if not custom_constraint_description.strip():
            st.warning(
                "Enter a constraint before starting the audit."
            )
            st.stop()

        # Build a real runtime semantic constraint from
        # the user-provided constraint description.
        custom_constraint = Constraint.from_semantic(
            constraint_id="CUSTOM-SEMANTIC",
            description=custom_constraint_description.strip(),
            risk_level=RiskLevel.HIGH,
            metadata={
                "source": "custom_prompt",
                "category": "user_defined",
            },
        )

        custom_test_case = AuditTestCase(
            test_id="custom-user-prompt",
            prompt=custom_prompt.strip(),
            constraints=[custom_constraint],
        )

        selected_test_cases = [custom_test_case]

    elif not selected_test_cases:

        st.warning(
            "Select at least one prompt."
        )
        st.stop()

    # ---------------------------------------------------------------
    # Reset response records for this audit
    # ---------------------------------------------------------------

    response_records = {}

    audit_runs = []

    overall_progress = st.progress(
        0,
        text="Preparing audit...",
    )

    total_models = len(selected_models)

    for model_index, model_name in enumerate(
        selected_models,
        start=1,
    ):

        st.write(
            f"### Running {model_name}"
        )

        model_progress = st.progress(
            0,
            text=f"Starting {model_name}...",
        )

        status_placeholder = st.empty()

        def update_progress(
            completed,
            total,
            test_id,
            latency_ms,
        ):
            percentage = (
                completed / total
                if total
                else 1.0
            )

            model_progress.progress(
                percentage,
                text=(
                    f"{model_name}: "
                    f"{completed}/{total} "
                    f"tests completed"
                ),
            )

            status_placeholder.caption(
                f"Latest test: `{test_id}` "
                f"| Model latency: "
                f"{latency_ms:.2f} ms"
            )

        try:

            if model_name.startswith("openai/"):
              model = GroqAdapter(model_name)
            else:
              model = OllamaAdapter(model_name)

            # -------------------------------------------------------
            # Custom prompt:
            #
            # We execute directly once so the dashboard can retain
            # and display the actual model response.
            #
            # Existing JBB audits continue to use run_model().
            # -------------------------------------------------------

            if is_custom_audit:

                start = time.perf_counter()

                response = model.generate(
                    custom_test_case.prompt
                )

                elapsed_ms = (
                    time.perf_counter() - start
                ) * 1000

                from app.evaluation.evaluator import Evaluator

                evaluator = Evaluator()

                result = evaluator.evaluate(
                    test_id=custom_test_case.test_id,
                    model=model.name,
                    response=response,
                    constraints=custom_test_case.constraints,
                )

                model_run_results = [result]

                response_records[
                    model_name
                ] = {
                    custom_test_case.test_id: {
                        "response": response,
                        "latency_ms": elapsed_ms,
                        "prompt": custom_test_case.prompt,
                        "constraint": (
                            custom_constraint_description.strip()
                        ),
                    }
                }

                model_average_latency = round(
                    elapsed_ms,
                    2,
                )

                model_progress.progress(
                    1.0,
                    text=(
                        f"{model_name}: "
                        "completed custom prompt"
                    ),
                )

                status_placeholder.caption(
                    f"Custom prompt completed "
                    f"| Model latency: "
                    f"{elapsed_ms:.2f} ms"
                )

            else:

                model_run = run_model(
                    model=model,
                    test_cases=selected_test_cases,
                    progress_callback=update_progress,
                )

                model_run_results = model_run.results
                model_average_latency = (
                    model_run.average_latency_ms
                )

            # -------------------------------------------------------
            # Audit run metadata
            # -------------------------------------------------------

            timestamp = datetime.now(
                timezone.utc
            ).strftime(
                "%Y%m%d%H%M%S%f"
            )

            run_prefix = (
                "custom"
                if is_custom_audit
                else "interactive"
            )

            audit_runs.append(
                {
                    "model": model_name,
                    "results": model_run_results,
                    "run_id": (
                        f"{run_prefix}-"
                        f"{model_name.replace('/', '-')}-"
                        f"{timestamp}"
                    ),
                    "average_latency_ms": (
                        model_average_latency
                    ),
                }
            )

        except Exception as exc:

            st.error(
                f"Audit failed for "
                f"{model_name}: {exc}"
            )

            continue

        overall_percentage = (
            model_index / total_models
        )

        overall_progress.progress(
            overall_percentage,
            text=(
                f"Completed "
                f"{model_index}/{total_models} models"
            ),
        )

    if not audit_runs:

        st.error(
            "No audit runs completed."
        )
        st.stop()

    # ---------------------------------------------------------------
    # Save response records
    # ---------------------------------------------------------------

    if is_custom_audit:

        st.session_state.current_response_records = (
            response_records
        )

    else:

        st.session_state.current_response_records = {}


    # ---------------------------------------------------------------
    # Model summaries
    # ---------------------------------------------------------------

    audit_summaries = compare_models(
        audit_runs
    )


# ---------------------------------------------------------------
# Regression state
# ---------------------------------------------------------------

if "audit_runs" in locals() and audit_runs:

    if st.session_state.previous_audit_runs is None:

        # First completed audit becomes the baseline.
        st.session_state.previous_audit_runs = audit_runs
        st.session_state.previous_response_records = (
            response_records
        )

        st.session_state.current_audit_runs = None
        st.session_state.current_response_records = {}

        is_baseline_run = True

    else:

        # If a current run already exists, it becomes the
        # baseline for this newly completed audit.
        if st.session_state.current_audit_runs is not None:

            st.session_state.previous_audit_runs = (
                st.session_state.current_audit_runs
            )

            st.session_state.previous_response_records = (
                st.session_state.current_response_records
            )

        # The newly completed audit becomes the current run.
        st.session_state.current_audit_runs = audit_runs
        st.session_state.current_response_records = (
            response_records
        )

        is_baseline_run = False

else:

    # No new audit was completed during this Streamlit run.
    is_baseline_run = False


   # ---------------------------------------------------------------
# Persistent storage
# ---------------------------------------------------------------

if "audit_runs" in locals() and audit_runs:

    results_store = ResultsStore()

    for audit_run in audit_runs:

        summary = next(
            item
            for item in audit_summaries
            if item["model"] == audit_run["model"]
        )

        results_store.save_evaluation_results(
            run_id=audit_run["run_id"],
            model=audit_run["model"],
            created_at=datetime.now(
                timezone.utc
            ).isoformat(),
            results=audit_run["results"],
            risk_rate=summary["risk_rate"],
            security_score=summary["security_score"],
        )


   # ---------------------------------------------------------------
# Completion message
# ---------------------------------------------------------------

if "audit_runs" in locals() and audit_runs:

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
# Display most recent audit
# -------------------------------------------------------------------

if (
    st.session_state.current_audit_runs
    is not None
):

    displayed_runs = (
        st.session_state.current_audit_runs
    )

    displayed_response_records = (
        st.session_state.current_response_records
    )

elif (
    st.session_state.previous_audit_runs
    is not None
):

    displayed_runs = (
        st.session_state.previous_audit_runs
    )

    displayed_response_records = (
        st.session_state.previous_response_records
    )

else:

    displayed_runs = None
    displayed_response_records = {}


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

    st.subheader("Per-Test Results")

    for audit_run in displayed_runs:

        model_name = audit_run["model"]

        st.write(
            f"### {model_name}"
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
                f"**{result.test_id}** — "
                f"{status}"
            )

            st.write(
                f"Risk: "
                f"{score.risk_rate:.2f}% | "
                f"Security: "
                f"{score.security_score:.2f}% | "
                f"Violations: "
                f"{score.violation_count}"
            )

            # -------------------------------------------------------
            # Custom model response
            # -------------------------------------------------------

            model_records = (
                displayed_response_records.get(
                    model_name,
                    {},
                )
            )

            response_record = (
                model_records.get(
                    result.test_id
                )
            )

            if response_record:

                with st.expander(
                    f"View model response — "
                    f"{result.test_id}",
                    expanded=True,
                ):

                    st.write("**Prompt**")

                    st.code(
                        response_record["prompt"],
                        language="text",
                    )

                    st.write(
                        "**Model response**"
                    )

                    st.code(
                        response_record["response"],
                        language="text",
                    )

                    st.caption(
                        f"Model latency: "
                        f"{response_record['latency_ms']:.2f} ms"
                    )

                    if response_record.get(
                        "constraint"
                    ):

                        st.write(
                            "**User-specified constraint**"
                        )

                        st.info(
                            response_record["constraint"]
                        )

            # -------------------------------------------------------
            # Violations
            # -------------------------------------------------------

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
# Regression Testing
# -------------------------------------------------------------------

st.subheader("Regression Testing")

if (
    st.session_state.previous_audit_runs is not None
    and st.session_state.current_audit_runs is not None
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
        set(previous_models)
        & set(current_models)
    )

    if common_models:

        regression_model = st.selectbox(
            "Select model for regression comparison:",
            options=common_models,
            key="regression_model_select",
        )

        baseline_run = previous_models[
            regression_model
        ]

        current_run = current_models[
            regression_model
        ]

        regression_result = compare_runs(
            baseline_run["results"],
            current_run["results"],
        )

        st.write(
            "Compared tests: "
            f"{regression_result['compared_count']}"
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Fixed",
            len(
                regression_result["fixed"]
            ),
        )

        col2.metric(
            "New Failures",
            len(
                regression_result["new_failures"]
            ),
        )

        col3.metric(
            "Persistent Failures",
            len(
                regression_result["persistent_failures"]
            ),
        )

        col4.metric(
            "Unchanged",
            len(
                regression_result["unchanged"]
            ),
        )

        if regression_result["fixed"]:

            st.write(
                "**Fixed:** "
                + ", ".join(
                    regression_result["fixed"]
                )
            )

        if regression_result["new_failures"]:

            st.write(
                "**New Failures:** "
                + ", ".join(
                    regression_result["new_failures"]
                )
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
                + ", ".join(
                    regression_result["unchanged"]
                )
            )

    else:

        st.info(
            "No common models are available for "
            "regression comparison."
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

stored_runs = history_store.list_runs()

if stored_runs:

    history_rows = []

    for run in stored_runs:

        history_rows.append(
            {
                "Run ID": run["run_id"],
                "Model": run["model"],
                "Created At": run["created_at"],
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