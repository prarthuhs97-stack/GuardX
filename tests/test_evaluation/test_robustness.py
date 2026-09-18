import pytest

from app.constraints.constraint import Constraint, ConstraintType
from app.evaluation.evaluator import Evaluator


def test_empty_response_fails_required_constraint():
    constraint = Constraint(
        constraint_id="required-1",
        type=ConstraintType.REQUIRED_KEYWORD,
        value="Python",
    )

    result = Evaluator().evaluate(
        test_id="edge-empty",
        model="test-model",
        response="",
        constraints=[constraint],
    )

    assert result.passed is False
    assert result.failed == ["required-1"]
    assert len(result.violations) == 1


def test_multiple_constraints_collect_all_violations():
    constraints = [
        Constraint(
            constraint_id="required-1",
            type=ConstraintType.REQUIRED_KEYWORD,
            value="Python",
        ),
        Constraint(
            constraint_id="forbidden-1",
            type=ConstraintType.FORBIDDEN_KEYWORD,
            value="Java",
        ),
        Constraint(
            constraint_id="length-1",
            type=ConstraintType.MAX_WORDS,
            value=2,
        ),
    ]

    result = Evaluator().evaluate(
        test_id="edge-multiple",
        model="test-model",
        response="Java is a programming language with many features.",
        constraints=constraints,
    )

    assert result.passed is False
    assert set(result.failed) == {"required-1", "forbidden-1", "length-1"}
    assert len(result.violations) == 3


def test_unsupported_constraint_type_raises_error():
    constraint = Constraint(
        constraint_id="unsupported-1",
        type=ConstraintType.FORMAT,
        value="json",
    )

    with pytest.raises(
        NotImplementedError,
        match="No checker implemented for constraint type",
    ):
        Evaluator().evaluate(
            test_id="edge-unsupported",
            model="test-model",
            response="test response",
            constraints=[constraint],
        )


def test_semantic_constraint_uses_checker(monkeypatch):
    def fake_semantic_check(response, constraint):
        return False

    monkeypatch.setattr(
        "app.evaluation.evaluator.check_semantic",
        fake_semantic_check,
    )

    constraint = Constraint(
        constraint_id="semantic-1",
        type=ConstraintType.SEMANTIC,
        value="beginner-friendly",
        description="The response must be beginner-friendly.",
    )

    result = Evaluator().evaluate(
        test_id="edge-semantic",
        model="test-model",
        response="Technical response.",
        constraints=[constraint],
    )

    assert result.passed is False
    assert result.failed == ["semantic-1"]
    assert len(result.violations) == 1
