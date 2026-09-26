from app.evaluation.result import EvaluationResult, Violation
from storage.serialization import evaluation_result_to_dict


def test_evaluation_result_serializes_to_json_safe_dict():
    result = EvaluationResult(
        test_id="T001",
        model="model-a",
        response="Synthetic response",
        passed=False,
        failed=["C1"],
        violations=[
            Violation(
                constraint_id="C1",
                constraint_type="forbidden_keyword",
                risk_level="high",
                description="Synthetic secret exposed",
                expected="Secret must not appear",
                actual="FAKE_SECRET_123",
            )
        ],
    )

    serialized = evaluation_result_to_dict(result)

    assert serialized["test_id"] == "T001"
    assert serialized["model"] == "model-a"
    assert serialized["passed"] is False
    assert serialized["failed"] == ["C1"]
    assert len(serialized["violations"]) == 1
    assert serialized["violations"][0]["risk_level"] == "high"