from app.constraints.constraint import Constraint, ConstraintType
from app.constraints.checkers.keyword_checker import (
    check_forbidden_keyword,
    check_required_keyword,
)


def test_required_keyword_present():
    constraint = Constraint(
        "C001",
        ConstraintType.REQUIRED_KEYWORD,
        "Python",
    )

    assert check_required_keyword("I use Python for automation.", constraint) is True


def test_required_keyword_missing():
    constraint = Constraint(
        "C002",
        ConstraintType.REQUIRED_KEYWORD,
        "Python",
    )

    assert check_required_keyword("I use Java for automation.", constraint) is False


def test_required_keyword_case_insensitive():
    constraint = Constraint(
        "C003",
        ConstraintType.REQUIRED_KEYWORD,
        "python",
    )

    assert check_required_keyword("Python is useful.", constraint) is True


def test_forbidden_keyword_absent():
    constraint = Constraint(
        "C004",
        ConstraintType.FORBIDDEN_KEYWORD,
        "eval",
    )

    assert check_forbidden_keyword("Use a safe function instead.", constraint) is True


def test_forbidden_keyword_present():
    constraint = Constraint(
        "C005",
        ConstraintType.FORBIDDEN_KEYWORD,
        "eval",
    )

    assert check_forbidden_keyword("The code uses eval.", constraint) is False


def test_forbidden_keyword_case_insensitive():
    constraint = Constraint(
        "C006",
        ConstraintType.FORBIDDEN_KEYWORD,
        "eval",
    )

    assert check_forbidden_keyword("The code uses EVAL.", constraint) is False