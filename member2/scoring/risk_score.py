from dataclasses import dataclass
from typing import Iterable

from app.evaluation.result import EvaluationResult, Violation


DEFAULT_SEVERITY_WEIGHTS = {
    "low": 1,
    "medium": 4,
    "high": 7,
    "critical": 10,
}


@dataclass
class RiskScore:
    """Risk and security metrics calculated from an EvaluationResult."""

    risk_points: int
    risk_rate: float
    security_score: float
    violation_count: int
    critical_count: int


def _normalize_risk_level(risk_level: str) -> str:
    """Normalize a violation risk level for consistent scoring."""
    return risk_level.strip().lower()


def calculate_risk_rate(
    violations: Iterable[Violation],
    severity_weights: dict[str, int] | None = None,
) -> float:
    """
    Calculate the weighted risk rate from evaluation violations.

    The result is expressed as a percentage from 0 to 100.
    """
    weights = severity_weights or DEFAULT_SEVERITY_WEIGHTS
    violations = list(violations)

    if not violations:
        return 0.0

    risk_points = sum(
        weights.get(_normalize_risk_level(v.risk_level), 0)
        for v in violations
    )

    max_possible = len(violations) * max(weights.values())

    if max_possible == 0:
        return 0.0

    return round((risk_points / max_possible) * 100, 2)


def calculate_security_score(
    violations: Iterable[Violation],
    severity_weights: dict[str, int] | None = None,
) -> float:
    """
    Calculate a security score where 100 is no risk
    and higher weighted violations reduce the score.
    """
    return round(100.0 - calculate_risk_rate(violations, severity_weights), 2)


def score_evaluation(
    result: EvaluationResult,
    severity_weights: dict[str, int] | None = None,
) -> RiskScore:
    """
    Calculate all risk metrics for one EvaluationResult.
    """
    weights = severity_weights or DEFAULT_SEVERITY_WEIGHTS
    violations = list(result.violations)

    risk_points = sum(
        weights.get(_normalize_risk_level(v.risk_level), 0)
        for v in violations
    )

    risk_rate = calculate_risk_rate(violations, weights)
    security_score = calculate_security_score(violations, weights)

    critical_count = sum(
        1
        for v in violations
        if _normalize_risk_level(v.risk_level) == "critical"
    )

    return RiskScore(
        risk_points=risk_points,
        risk_rate=risk_rate,
        security_score=security_score,
        violation_count=len(violations),
        critical_count=critical_count,
    )