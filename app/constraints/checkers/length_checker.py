from app.constraints.constraint import Constraint, ConstraintType


def check_max_words(response: str, constraint: Constraint) -> bool:
    """Return True when the response does not exceed the maximum word count."""
    if constraint.type != ConstraintType.MAX_WORDS:
        raise ValueError("Constraint must be a max words constraint.")

    max_words = int(constraint.value)
    word_count = len(response.split())

    return word_count <= max_words


def check_min_words(response: str, constraint: Constraint) -> bool:
    """Return True when the response meets the minimum word count."""
    if constraint.type != ConstraintType.MIN_WORDS:
        raise ValueError("Constraint must be a min words constraint.")

    min_words = int(constraint.value)
    word_count = len(response.split())

    return word_count >= min_words


def check_max_characters(response: str, constraint: Constraint) -> bool:
    """Return True when the response does not exceed the maximum character count."""
    if constraint.type != ConstraintType.MAX_CHARACTERS:
        raise ValueError("Constraint must be a max characters constraint.")

    max_characters = int(constraint.value)

    return len(response) <= max_characters


def check_max_lines(response: str, constraint: Constraint) -> bool:
    """Return True when the response does not exceed the maximum line count."""
    if constraint.type != ConstraintType.MAX_LINES:
        raise ValueError("Constraint must be a max lines constraint.")

    max_lines = int(constraint.value)
    line_count = len(response.splitlines())

    return line_count <= max_lines