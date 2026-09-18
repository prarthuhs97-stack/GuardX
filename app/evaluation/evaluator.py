from app.constraints.constraint import Constraint, ConstraintType
from app.constraints.checkers.code_checker import check_code_restriction
from app.constraints.checkers.format_checker import check_bullet_count
from app.constraints.checkers.keyword_checker import (
    check_forbidden_keyword,
    check_required_keyword,
)
from app.constraints.checkers.length_checker import (
    check_max_characters,
    check_max_lines,
    check_max_words,
    check_min_words,
)
from app.evaluation.result import EvaluationResult, Violation


class Evaluator:
    """Evaluate an LLM response against a collection of constraints."""

    def evaluate(
        self,
        test_id: str,
        model: str,
        response: str,
        constraints: list[Constraint],
    ) -> EvaluationResult:
        violations = []
        failed = []

        for constraint in constraints:
            passed = self._check_constraint(response, constraint)

            if not passed:
                failed.append(constraint.constraint_id)
                violations.append(
                    Violation(
                        constraint_id=constraint.constraint_id,
                        constraint_type=constraint.type.value,
                        risk_level=constraint.risk_level.value,
                        description=constraint.description,
                        expected=constraint.value,
                        actual=response,
                    )
                )

        return EvaluationResult(
            test_id=test_id,
            model=model,
            response=response,
            constraints=constraints,
            passed=len(violations) == 0,
            failed=failed,
            violations=violations,
        )

    def _check_constraint(
        self,
        response: str,
        constraint: Constraint,
    ) -> bool:
        checkers = {
            ConstraintType.REQUIRED_KEYWORD: check_required_keyword,
            ConstraintType.FORBIDDEN_KEYWORD: check_forbidden_keyword,
            ConstraintType.MAX_WORDS: check_max_words,
            ConstraintType.MIN_WORDS: check_min_words,
            ConstraintType.MAX_CHARACTERS: check_max_characters,
            ConstraintType.MAX_LINES: check_max_lines,
            ConstraintType.BULLET_COUNT: check_bullet_count,
            ConstraintType.CODE_RESTRICTION: check_code_restriction,
        }

        checker = checkers.get(constraint.type)

        if checker is None:
            raise NotImplementedError(
                f"No checker implemented for constraint type: {constraint.type.value}"
            )

        return checker(response, constraint)
