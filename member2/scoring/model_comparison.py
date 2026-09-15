from typing import Any


def summarize_model_run(run: dict[str, Any]) -> dict[str, Any]:
    """Create comparable metrics from one model audit run."""
    results = run.get("results", [])
    total = len(results)
    failures = sum(1 for result in results if not result.get("passed", False))

    return {
        "model": run.get("model", "unknown"),
        "run_id": run.get("run_id", "unknown"),
        "total_tests": total,
        "failed_tests": failures,
        "passed_tests": total - failures,
        "attack_success_rate": round((failures / total) * 100, 2) if total else 0.0,
        "security_score": run.get("security_score"),
        "risk_rate": run.get("risk_rate"),
        "average_latency_ms": run.get("average_latency_ms"),
    }


def compare_models(runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return normalized summaries for multiple model runs."""
    return [summarize_model_run(run) for run in runs]
