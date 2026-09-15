from app.constraints.constraint import Constraint, ConstraintType


def check_bullet_count(response: str, constraint: Constraint) -> bool:
    """Return True when the response contains the required number of bullet points."""
    if constraint.type != ConstraintType.BULLET_COUNT:
        raise ValueError("Constraint must be a bullet count constraint.")

    expected_count = int(constraint.value)

    bullet_count = sum(
        1
        for line in response.splitlines()
        if line.strip().startswith(("-", "*", "•"))
    )

    return bullet_count == expected_count