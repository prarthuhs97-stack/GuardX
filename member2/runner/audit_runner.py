from dataclasses import dataclass

from app.constraints.constraint import Constraint
from app.evaluation.evaluator import Evaluator
from app.evaluation.result import EvaluationResult
from app.models.base import LLMModel


@dataclass
class AuditTestCase:
    """A single GuardX prompt and its expected constraints."""

    test_id: str
    prompt: str
    constraints: list[Constraint]


def run_test_case(
    model: LLMModel,
    test_case: AuditTestCase,
    evaluator: Evaluator | None = None,
) -> EvaluationResult:
    """Generate a model response and evaluate it against the test case."""

    evaluator = evaluator or Evaluator()

    response = model.generate(test_case.prompt)

    return evaluator.evaluate(
        test_id=test_case.test_id,
        model=model.name,
        response=response,
        constraints=test_case.constraints,
    )


def run_test_cases(
    model: LLMModel,
    test_cases: list[AuditTestCase],
    evaluator: Evaluator | None = None,
) -> list[EvaluationResult]:
    """Run multiple test cases against one model."""

    evaluator = evaluator or Evaluator()

    return [
        run_test_case(
            model=model,
            test_case=test_case,
            evaluator=evaluator,
        )
        for test_case in test_cases
    ]