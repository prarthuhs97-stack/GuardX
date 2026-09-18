from app.evaluation.result import EvaluationResult, Violation


def test_evaluation_result_creation():
    violation = Violation(
        constraint_id="C001",
        constraint_type="forbidden_keyword",
        risk_level="high",
        description="The response must not use eval",
        expected="eval absent",
        actual="eval found",
    )

    result = EvaluationResult(
        test_id="T001",
        model="test-model",
        response="x = eval(input())",
        constraints=["C001"],
        passed=False,
        failed=["C001"],
        violations=[violation],
    )

    assert result.test_id == "T001"
    assert result.model == "test-model"
    assert result.passed is False
    assert result.failed == ["C001"]
    assert len(result.violations) == 1
    assert result.violations[0].risk_level == "high"


def test_evaluation_result_defaults():
    result = EvaluationResult(
        test_id="T002",
        model="test-model",
        response="Valid response",
    )

    assert result.passed is True
    assert result.constraints == []
    assert result.failed == []
    assert result.violations == []
