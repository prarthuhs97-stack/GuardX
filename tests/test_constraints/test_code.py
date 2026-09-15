from app.constraints.constraint import Constraint, ConstraintType
from app.constraints.checkers.code_checker import check_code_restriction


def test_forbidden_keyword_passes():
    constraint = Constraint(
        "C001",
        ConstraintType.CODE_RESTRICTION,
        "forbidden_keyword:eval",
    )

    response = "x = 10\nprint(x)"

    assert check_code_restriction(response, constraint) is True


def test_forbidden_keyword_fails():
    constraint = Constraint(
        "C002",
        ConstraintType.CODE_RESTRICTION,
        "forbidden_keyword:eval",
    )

    response = "x = eval(input())"

    assert check_code_restriction(response, constraint) is False


def test_forbidden_import_passes():
    constraint = Constraint(
        "C003",
        ConstraintType.CODE_RESTRICTION,
        "forbidden_import:os",
    )

    response = "import math\nprint(math.sqrt(4))"

    assert check_code_restriction(response, constraint) is True


def test_forbidden_import_fails():
    constraint = Constraint(
        "C004",
        ConstraintType.CODE_RESTRICTION,
        "forbidden_import:os",
    )

    response = "import os\nprint(os.getcwd())"

    assert check_code_restriction(response, constraint) is False


def test_forbidden_from_import_fails():
    constraint = Constraint(
        "C005",
        ConstraintType.CODE_RESTRICTION,
        "forbidden_import:os",
    )

    response = "from os import path"

    assert check_code_restriction(response, constraint) is False


def test_invalid_code_fails():
    constraint = Constraint(
        "C006",
        ConstraintType.CODE_RESTRICTION,
        "forbidden_import:os",
    )

    response = "import os\nif"

    assert check_code_restriction(response, constraint) is False