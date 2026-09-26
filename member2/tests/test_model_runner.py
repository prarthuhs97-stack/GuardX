from app.constraints.constraint import (
    Constraint,
    ConstraintType,
    RiskLevel,
)

from runner.audit_runner import AuditTestCase
from runner.model_runner import run_model


class FakeModel:
    name = "fake-model"

    def generate(self, prompt: str) -> str:
        return "This is a safe response."


def test_run_model_returns_results_and_latency():
    test_cases = [
        AuditTestCase(
            test_id="T001",
            prompt="Test prompt",
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
    ]

    run = run_model(
        model=FakeModel(),
        test_cases=test_cases,
    )

    assert run.model == "fake-model"
    assert len(run.results) == 1
    assert run.results[0].test_id == "T001"
    assert run.results[0].passed is True
    assert run.average_latency_ms >= 0