from typing import Any

from app.evaluation.result import EvaluationResult

from scoring.risk_score import score_evaluation


def summarize_model_run(
    model: str,
    results: list[EvaluationResult],
    run_id: str = "unknown",
    average_latency_ms: float | None = None,
) -> dict[str, Any]:
    """Create comparable metrics from EvaluationResult objects."""

    total = len(results)
    failed_tests = sum(1 for result in results if not result.passed)

    scores = [score_evaluation(result) for result in results]

    total_risk_points = sum(score.risk_points for score in scores)
    total_violations = sum(score.violation_count for score in scores)
    critical_violations = sum(score.critical_count for score in scores)

    if total:
        risk_rate = round(
            sum(score.risk_rate for score in scores) / total,
            2,
        )
        security_score = round(
            sum(score.security_score for score in scores) / total,
            2,
        )
    else:
        risk_rate = 0.0
        security_score = 100.0

    return {
        "model": model,
        "run_id": run_id,
        "total_tests": total,
        "failed_tests": failed_tests,
        "passed_tests": total - failed_tests,
        "attack_success_rate": round(
            (failed_tests / total) * 100, 2
        ) if total else 0.0,
        "total_violations": total_violations,
        "critical_violations": critical_violations,
        "total_risk_points": total_risk_points,
        "risk_rate": risk_rate,
        "security_score": security_score,
        "average_latency_ms": average_latency_ms,
    }


def compare_models(
    runs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Compare multiple model runs using standardized EvaluationResult objects.

    Each run must contain:
        model: model name
        results: list[EvaluationResult]

    Optional:
        run_id
        average_latency_ms
    """
    summaries = []

    for run in runs:
        summaries.append(
            summarize_model_run(
                model=run.get("model", "unknown"),
                results=run.get("results", []),
                run_id=run.get("run_id", "unknown"),
                average_latency_ms=run.get("average_latency_ms"),
            )
        )

    return summaries