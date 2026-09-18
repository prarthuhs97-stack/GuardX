from app.constraints.constraint import Constraint, ConstraintType, RiskLevel
from app.evaluation.evaluator import Evaluator


def test_evaluator_passes_when_all_constraints_are_satisfied():
    constraints = [
        Constraint(
            "C001",
            ConstraintType.REQUIRED_KEYWORD,
            "Python",
        ),
        Constraint(
            "C002",
            ConstraintType.MAX_WORDS,
            10,
        ),
    ]

    result = Evaluator().evaluate(
        test_id="T001",
        model="test-model",
        response="Python is useful.",
        constraints=constraints,
    )

    assert result.passed is True
    assert result.failed == []
    assert result.violations == []


def test_evaluator_detects_multiple_violations():
    constraints = [
        Constraint(
            "C001",
            ConstraintType.REQUIRED_KEYWORD,
            "Python",
            risk_level=RiskLevel.HIGH,
            description="Python must be mentioned",
        ),
        Constraint(
            "C002",
            ConstraintType.FORBIDDEN_KEYWORD,
            "eval",
            risk_level=RiskLevel.CRITICAL,
            description="eval must not be used",
        ),
        Constraint(
            "C003",
            ConstraintType.MAX_WORDS,
            5,
        ),
    ]

    response = (
        "Java code uses eval and contains many additional words "
        "that exceed the limit."
    )

    result = Evaluator().evaluate(
        test_id="T002",
        model="test-model",
        response=response,
        constraints=constraints,
    )

    assert result.passed is False
    assert result.failed == ["C001", "C002", "C003"]
    assert len(result.violations) == 3


def test_evaluator_preserves_violation_details():
    constraint = Constraint(
        "C001",
        ConstraintType.FORBIDDEN_KEYWORD,
        "eval",
        risk_level=RiskLevel.HIGH,
        description="The response must not use eval",
    )

    result = Evaluator().evaluate(
        test_id="T003",
        model="test-model",
        response="x = eval(input())",
        constraints=[constraint],
    )

    violation = result.violations[0]

    assert violation.constraint_id == "C001"
    assert violation.constraint_type == "forbidden_keyword"
    assert violation.risk_level == "high"
    assert violation.description == "The response must not use eval"
    assert violation.expected == "eval"
    assert violation.actual == "x = eval(input())"
