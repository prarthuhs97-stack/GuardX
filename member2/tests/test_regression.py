from app.evaluation.result import EvaluationResult, Violation
from regression.comparison import compare_runs


def make_result(
    test_id: str,
    passed: bool,
    risk_level: str | None = None,
) -> EvaluationResult:
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


def test_regression_detects_fixed_and_new_failures():
    baseline = [
        make_result("T1", False, "high"),
        make_result("T2", True),
    ]

    current = [
        make_result("T1", True),
        make_result("T2", False, "medium"),
    ]

    result = compare_runs(baseline, current)

    assert result["fixed"] == ["T1"]
    assert result["new_failures"] == ["T2"]


def test_regression_detects_persistent_failures():
    baseline = [
        make_result("T1", False, "high"),
        make_result("T2", True),
    ]

    current = [
        make_result("T1", False, "critical"),
        make_result("T2", True),
    ]

    result = compare_runs(baseline, current)

    assert result["persistent_failures"] == ["T1"]
    assert result["unchanged"] == ["T2"]


def test_regression_ignores_tests_missing_from_one_run():
    baseline = [
        make_result("T1", False, "high"),
        make_result("T2", True),
    ]

    current = [
        make_result("T1", True),
        make_result("T3", False, "critical"),
    ]

    result = compare_runs(baseline, current)

    assert result["fixed"] == ["T1"]
    assert result["compared_count"] == 1
    assert result["baseline_count"] == 2
    assert result["current_count"] == 2