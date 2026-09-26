import time
from dataclasses import dataclass
from typing import Callable

from app.evaluation.evaluator import Evaluator
from app.evaluation.result import EvaluationResult
from app.models.base import LLMModel
from runner.audit_runner import AuditTestCase


@dataclass
class ModelRun:
    model: str
    results: list[EvaluationResult]
    average_latency_ms: float


def run_model(
    model: LLMModel,
    test_cases: list[AuditTestCase],
    evaluator: Evaluator | None = None,
    progress_callback: Callable[[int, int, str, float], None] | None = None,
) -> ModelRun:
    """
    Run an audit against a model.

    progress_callback, when provided, receives:
        completed_count,
        total_count,
        test_id,
        latency_ms
    """

    evaluator = evaluator or Evaluator()

    results = []
    latencies = []

    total = len(test_cases)

    for index, test_case in enumerate(
        test_cases,
        start=1,
    ):
        start = time.perf_counter()

        response = model.generate(
            test_case.prompt
        )

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        latencies.append(elapsed_ms)

        result = evaluator.evaluate(
            test_id=test_case.test_id,
            model=model.name,
            response=response,
            constraints=test_case.constraints,
        )

        results.append(result)

        if progress_callback is not None:
            progress_callback(
                index,
                total,
                test_case.test_id,
                elapsed_ms,
            )

    average_latency_ms = (
        round(
            sum(latencies) / len(latencies),
            2,
        )
        if latencies
        else 0.0
    )

    return ModelRun(
        model=model.name,
        results=results,
        average_latency_ms=average_latency_ms,
    )