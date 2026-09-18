import time
from dataclasses import dataclass

from app.evaluation.evaluator import Evaluator
from app.evaluation.result import EvaluationResult
from app.models.base import LLMModel

from runner.audit_runner import AuditTestCase

from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelRun:
    """Results from running a set of audit tests against one model."""

    model: str
    results: list[EvaluationResult]
    average_latency_ms: float


def run_model(
    model: LLMModel,
    test_cases: list[AuditTestCase],
    evaluator: Evaluator | None = None,
) -> ModelRun:
    """Run GuardX test cases against a model and measure response latency."""

    evaluator = evaluator or Evaluator()

    results = []
    latencies = []

    for test_case in test_cases:
        start = time.perf_counter()

        response = model.generate(test_case.prompt)

        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

        result = evaluator.evaluate(
            test_id=test_case.test_id,
            model=model.name,
            response=response,
            constraints=test_case.constraints,
        )

        results.append(result)

    average_latency_ms = (
        round(sum(latencies) / len(latencies), 2)
        if latencies
        else 0.0
    )

    return ModelRun(
        model=model.name,
        results=results,
        average_latency_ms=average_latency_ms,
    )