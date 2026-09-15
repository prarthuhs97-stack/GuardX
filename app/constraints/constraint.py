from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ConstraintType(str, Enum):
    REQUIRED_KEYWORD = "required_keyword"
    FORBIDDEN_KEYWORD = "forbidden_keyword"
    MAX_WORDS = "max_words"
    MIN_WORDS = "min_words"
    MAX_CHARACTERS = "max_characters"
    MAX_LINES = "max_lines"
    BULLET_COUNT = "bullet_count"
    FORMAT = "format"
    CODE_RESTRICTION = "code_restriction"
    SEMANTIC = "semantic"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Constraint:
    constraint_id: str
    type: ConstraintType
    value: Any
    risk_level: RiskLevel = RiskLevel.MEDIUM
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
