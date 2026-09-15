from app.constraints.constraint import Constraint, ConstraintType
from app.constraints.checkers.format_checker import check_bullet_count


def test_bullet_count_passes():
    constraint = Constraint("C001", ConstraintType.BULLET_COUNT, 3)

    response = "- One\n- Two\n- Three"

    assert check_bullet_count(response, constraint) is True


def test_bullet_count_fails():
    constraint = Constraint("C002", ConstraintType.BULLET_COUNT, 3)

    response = "- One\n- Two"

    assert check_bullet_count(response, constraint) is False


def test_bullet_count_supports_different_bullet_symbols():
    constraint = Constraint("C003", ConstraintType.BULLET_COUNT, 3)

    response = "* One\n• Two\n- Three"

    assert check_bullet_count(response, constraint) is True