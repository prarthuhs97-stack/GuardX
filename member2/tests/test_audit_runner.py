from app.constraints.constraint import Constraint, ConstraintType, RiskLevel
from app.evaluation.evaluator import Evaluator

from runner.audit_runner import AuditTestCase, run_test_case


class FakeModel:
    name = "fake-model"

    def generate(self, prompt: str) -> str:
        return "This is a safe response."


def test_run_test_case_generates_and_evaluates_response():
    test_case = AuditTestCase(
        test_id="T001",
        prompt="Give me a safe response.",
        constraints=[
            Constraint(
                constraint_id="C001",
                type=ConstraintType.FORBIDDEN_KEYWORD,
                value="password",
                risk_level=RiskLevel.HIGH,
                description="Do not reveal passwords.",
            )
        ],
    )

    result = run_test_case(
        model=FakeModel(),
        test_case=test_case,
        evaluator=Evaluator(),
    )

    assert result.test_id == "T001"
    assert result.model == "fake-model"
    assert result.response == "This is a safe response."
    assert result.passed is True
    assert result.violations == []