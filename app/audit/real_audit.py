from datetime import datetime, timezone

from app.evaluation.evaluator import Evaluator
from app.models.base import LLMModel
from member2.datasets.jbb_loader import load_jbb_behaviors
from member2.runner.model_runner import ModelRun, run_model
from member2.scoring.model_comparison import summarize_model_run
from member2.storage.results_store import ResultsStore


def run_jbb_audit(
    model: LLMModel,
    dataset_path: str,
    limit: int | None = 3,
    run_id: str | None = None,
    store: ResultsStore | None = None,
) -> tuple[ModelRun, dict]:
    """Run a JBB harmful-behavior audit and optionally persist its results."""

    test_cases = load_jbb_behaviors(
        dataset_path,
        limit=limit,
        split="harmful",
    )

    run = run_model(
        model=model,
        test_cases=test_cases,
        evaluator=Evaluator(),
    )

    resolved_run_id = run_id or (
        f"{model.name}-"
        f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    )

    summary = summarize_model_run(
        model=run.model,
        results=run.results,
        run_id=resolved_run_id,
        average_latency_ms=run.average_latency_ms,
    )

    if store is not None:
        store.save_evaluation_results(
            run_id=resolved_run_id,
            model=run.model,
            created_at=datetime.now(timezone.utc).isoformat(),
            results=run.results,
            risk_rate=summary["risk_rate"],
            security_score=summary["security_score"],
        )

    return run, summary