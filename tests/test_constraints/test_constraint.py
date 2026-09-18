from app.constraints.constraint import Constraint, ConstraintType, RiskLevel


def test_constraint_creation():
    constraint = Constraint(
        constraint_id="C001",
        type=ConstraintType.FORBIDDEN_KEYWORD,
        value="eval",
        risk_level=RiskLevel.HIGH,
        description="The response must not use eval",
    )

    assert constraint.constraint_id == "C001"
    assert constraint.type == ConstraintType.FORBIDDEN_KEYWORD
    assert constraint.value == "eval"
    assert constraint.risk_level == RiskLevel.HIGH
    assert constraint.description == "The response must not use eval"


def test_constraint_default_values():
    constraint = Constraint(
        constraint_id="C002",
        type=ConstraintType.MAX_WORDS,
        value=100,
    )

    assert constraint.risk_level == RiskLevel.MEDIUM
    assert constraint.description == ""
    assert constraint.metadata == {}