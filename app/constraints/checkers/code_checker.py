import ast

from app.constraints.constraint import Constraint, ConstraintType


def check_code_restriction(response: str, constraint: Constraint) -> bool:
    """Return True when the code does not violate the specified restriction."""
    if constraint.type != ConstraintType.CODE_RESTRICTION:
        raise ValueError("Constraint must be a code restriction constraint.")

    restriction = str(constraint.value).strip()

    if not restriction:
        return True

    try:
        tree = ast.parse(response)
    except SyntaxError:
        return False

    if restriction.startswith("forbidden_keyword:"):
        keyword = restriction.split(":", 1)[1].strip()

        if not keyword:
            return True

        return keyword not in response

    if restriction.startswith("forbidden_import:"):
        module_name = restriction.split(":", 1)[1].strip()

        if not module_name:
            return True

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == module_name:
                        return False

            if isinstance(node, ast.ImportFrom):
                if node.module == module_name:
                    return False

        return True

    return True