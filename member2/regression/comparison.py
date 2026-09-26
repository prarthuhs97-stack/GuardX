from typing import Any

from app.evaluation.result import EvaluationResult


def index_results(
    results: list[EvaluationResult],
) -> dict[str, EvaluationResult]:
    """Index evaluation results by test ID."""
    return {result.test_id: result for result in results}


def compare_runs(
    baseline_results: list[EvaluationResult],
    current_results: list[EvaluationResult],
) -> dict[str, Any]:
    """
    Compare baseline and current evaluation runs.

    Categories:
    - fixed: baseline failed, current passed
    - new_failures: baseline passed, current failed
    - persistent_failures: both failed
    - unchanged: both passed
    """
    baseline = index_results(baseline_results)
    current = index_results(current_results)

    fixed = []
    new_failures = []
    persistent_failures = []
    unchanged = []

    common_test_ids = sorted(set(baseline) & set(current))

    for test_id in common_test_ids:
        old = baseline[test_id]
        new = current[test_id]

        if not old.passed and new.passed:
            fixed.append(test_id)
        elif old.passed and not new.passed:
            new_failures.append(test_id)
        elif not old.passed and not new.passed:
            persistent_failures.append(test_id)
        else:
            unchanged.append(test_id)

    return {
        "fixed": fixed,
        "new_failures": new_failures,
        "persistent_failures": persistent_failures,
        "unchanged": unchanged,
        "baseline_count": len(baseline_results),
        "current_count": len(current_results),
        "compared_count": len(common_test_ids),
    }