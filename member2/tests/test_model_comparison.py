from app.evaluation.result import EvaluationResult, Violation

from scoring.model_comparison import compare_models


def make_result(test_id: str, passed: bool, risk_level: str | None = None):
    violations = []

    if risk_level:
        violations.append(
            Violation(
                constraint_id="C1",
                constraint_type="keyword",
                risk_level=risk_level,
                description="Test violation",
                expected="No secret",
                actual="Synthetic secret exposed",
            )
        )

    return EvaluationResult(
        test_id=test_id,
        model="model-a",
        response="Test response",
        passed=passed,
        failed=[] if passed else ["C1"],
        violations=violations,
    )


def test_model_comparison_counts_failures():
    runs = [
        {
            "run_id": "r1",
            "model": "model-a",
            "results": [
                make_result("T1", True),
                make_result("T2", False, "high"),
            ],
        }
    ]

    summary = compare_models(runs)[0]

    assert summary["total_tests"] == 2
    assert summary["failed_tests"] == 1
    assert summary["passed_tests"] == 1
    assert summary["attack_success_rate"] == 50.0


def test_model_comparison_calculates_risk_metrics():
    runs = [
        {
            "run_id": "r2",
            "model": "model-a",
            "results": [
                make_result("T1", True),
                make_result("T2", False, "critical"),
            ],
        }
    ]

    summary = compare_models(runs)[0]

    assert summary["total_violations"] == 1
    assert summary["critical_violations"] == 1
    assert summary["total_risk_points"] == 10
    assert summary["risk_rate"] == 50.0
    assert summary["security_score"] == 50.0


def test_multiple_models_are_compared():
    runs = [
        {
            "run_id": "r1",
            "model": "model-a",
            "results": [
                make_result("T1", True),
            ],
        },
        {
            "run_id": "r2",
            "model": "model-b",
            "results": [
                make_result("T1", False, "medium"),
            ],
        },
    ]

    summaries = compare_models(runs)

    assert len(summaries) == 2
    assert summaries[0]["model"] == "model-a"
    assert summaries[1]["model"] == "model-b"
    assert summaries[0]["security_score"] == 100.0
    assert summaries[1]["critical_violations"] == 0