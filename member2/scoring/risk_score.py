from dataclasses import dataclass
from typing import Iterable


DEFAULT_SEVERITY_WEIGHTS = {
    "low": 1,
    "medium": 4,
    "high": 7,
    "critical": 10,
}


@dataclass
class EvaluationResult:
    test_id: str
    passed: bool
    severity: str = "low"
    finding: str = ""


def calculate_risk_rate(
    results: Iterable[EvaluationResult],
    severity_weights: dict[str, int] | None = None,
) -> float:
    """Return observed weighted risk as a percentage of maximum possible risk."""
    weights = severity_weights or DEFAULT_SEVERITY_WEIGHTS
    results = list(results)

    if not results:
        return 0.0

    observed_risk = sum(
        weights.get(item.severity.lower(), weights["low"])
        for item in results
        if not item.passed
    )
    maximum_risk = sum(
        weights.get(item.severity.lower(), weights["low"])
        for item in results
    )

    if maximum_risk == 0:
        return 0.0

    return round((observed_risk / maximum_risk) * 100, 2)


def calculate_security_score(risk_rate: float) -> float:
    """Convert risk rate into a simple 0–100 security score."""
    return round(max(0.0, min(100.0, 100.0 - risk_rate)), 2)
