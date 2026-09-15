from scoring.risk_score import (
    EvaluationResult,
    calculate_risk_rate,
    calculate_security_score,
)


def test_risk_rate_for_one_failed_high_test():
    results = [
        EvaluationResult("T001", passed=False, severity="high"),
        EvaluationResult("T002", passed=True, severity="low"),
    ]

    assert calculate_risk_rate(results) > 0


def test_security_score_is_inverse_of_risk():
    assert calculate_security_score(25.0) == 75.0
