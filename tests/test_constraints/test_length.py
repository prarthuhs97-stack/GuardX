from app.constraints.constraint import Constraint, ConstraintType
from app.constraints.checkers.length_checker import (
    check_max_words,
    check_min_words,
    check_max_characters,
    check_max_lines,
)


def test_max_words_passes():
    constraint = Constraint("C001", ConstraintType.MAX_WORDS, 5)

    assert check_max_words("Python is simple and powerful.", constraint) is True


def test_max_words_fails():
    constraint = Constraint("C002", ConstraintType.MAX_WORDS, 3)

    assert check_max_words("Python is simple and powerful.", constraint) is False


def test_min_words_passes():
    constraint = Constraint("C003", ConstraintType.MIN_WORDS, 4)

    assert check_min_words("Python is simple and powerful.", constraint) is True


def test_min_words_fails():
    constraint = Constraint("C004", ConstraintType.MIN_WORDS, 10)

    assert check_min_words("Python is simple and powerful.", constraint) is False


def test_max_characters_passes():
    constraint = Constraint("C005", ConstraintType.MAX_CHARACTERS, 40)

    assert check_max_characters("Python is simple.", constraint) is True


def test_max_characters_fails():
    constraint = Constraint("C006", ConstraintType.MAX_CHARACTERS, 5)

    assert check_max_characters("Python is simple.", constraint) is False


def test_max_lines_passes():
    constraint = Constraint("C007", ConstraintType.MAX_LINES, 2)

    assert check_max_lines("Line one\nLine two", constraint) is True


def test_max_lines_fails():
    constraint = Constraint("C008", ConstraintType.MAX_LINES, 2)

    assert check_max_lines("Line one\nLine two\nLine three", constraint) is False