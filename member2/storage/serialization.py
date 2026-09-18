from typing import Any

from app.evaluation.result import EvaluationResult


def evaluation_result_to_dict(result: EvaluationResult) -> dict[str, Any]:
    """Convert an EvaluationResult into JSON-serializable data."""

    return {
        "test_id": result.test_id,
        "model": result.model,
        "response": result.response,
        "passed": result.passed,
        "failed": list(result.failed),
        "violations": [
            {
                "constraint_id": violation.constraint_id,
                "constraint_type": violation.constraint_type,
                "risk_level": violation.risk_level,
                "description": violation.description,
                "expected": violation.expected,
                "actual": violation.actual,
            }
            for violation in result.violations
        ],
    }


def evaluation_results_to_dict(
    results: list[EvaluationResult],
) -> list[dict[str, Any]]:
    """Convert multiple EvaluationResult objects into JSON-safe dictionaries."""
    return [evaluation_result_to_dict(result) for result in results]