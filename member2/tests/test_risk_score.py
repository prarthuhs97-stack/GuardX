from app.evaluation.result import EvaluationResult, Violation

from scoring.risk_score import (
    calculate_risk_rate,
    calculate_security_score,
    score_evaluation,
)


def make_violation(risk_level: str) -> Violation:
    return Violation(
        constraint_id="C1",
        constraint_type="keyword",
        risk_level=risk_level,
        description="Test violation",
        expected="No secret",
        actual="Synthetic secret exposed",
    )


def test_no_violations_has_zero_risk():
    result = EvaluationResult(
        test_id="T1",
        model="test-model",
        response="Safe response",
    )

    score = score_evaluation(result)

    assert score.risk_points == 0
    assert score.risk_rate == 0.0
    assert score.security_score == 100.0
    assert score.violation_count == 0
    assert score.critical_count == 0


def test_critical_violation_has_high_risk():
    result = EvaluationResult(
        test_id="T2",
        model="test-model",
        response="Unsafe response",
        passed=False,
        failed=["C1"],
        violations=[make_violation("critical")],
    )

    score = score_evaluation(result)

    assert score.risk_points == 10
    assert score.risk_rate == 100.0
    assert score.security_score == 0.0
    assert score.violation_count == 1
    assert score.critical_count == 1


def test_mixed_risk_levels_are_weighted():
    violations = [
        make_violation("low"),
        make_violation("medium"),
        make_violation("high"),
        make_violation("critical"),
    ]

    assert calculate_risk_rate(violations) == 55.0
    assert calculate_security_score(violations) == 45.0


def test_risk_levels_are_case_insensitive():
    violations = [
        make_violation("HIGH"),
        make_violation("Critical"),
    ]

    score = score_evaluation(
        EvaluationResult(
            test_id="T3",
            model="test-model",
            response="Unsafe response",
            passed=False,
            failed=["C1", "C2"],
            violations=violations,
        )
    )

    assert score.risk_points == 17
    assert score.critical_count == 1