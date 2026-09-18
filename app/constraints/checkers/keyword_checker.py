from app.constraints.constraint import Constraint, ConstraintType


def check_required_keyword(response: str, constraint: Constraint) -> bool:
    """Return True when the required keyword is present in the response."""
    if constraint.type != ConstraintType.REQUIRED_KEYWORD:
        raise ValueError("Constraint must be a required keyword constraint.")

    keyword = str(constraint.value).strip()

    if not keyword:
        return False

    return keyword.lower() in response.lower()


def check_forbidden_keyword(response: str, constraint: Constraint) -> bool:
    """Return True when the forbidden keyword is NOT present in the response."""
    if constraint.type != ConstraintType.FORBIDDEN_KEYWORD:
        raise ValueError("Constraint must be a forbidden keyword constraint.")

    keyword = str(constraint.value).strip()

    if not keyword:
        return True

    return keyword.lower() not in response.lower()