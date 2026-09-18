from dataclasses import dataclass, field
from typing import Any


@dataclass
class Violation:
    constraint_id: str
    constraint_type: str
    risk_level: str
    description: str
    expected: Any
    actual: Any


@dataclass
class EvaluationResult:
    test_id: str
    model: str
    response: str
    constraints: list[Any] = field(default_factory=list)
    passed: bool = True
    failed: list[str] = field(default_factory=list)
    violations: list[Violation] = field(default_factory=list)
