# Auto generated code by script: json_schema_to_class.py
from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json

__all__ = ["GradingSubmission", "Gradings", "GradingTestCase", "GradingTestSuite"]


@dataclass_json
@dataclass
class GradingTestCase:
    name: str
    points: int
    comment: str


@dataclass_json
@dataclass
class GradingTestSuite:
    name: str
    test_cases: List[GradingTestCase]


@dataclass_json
@dataclass
class GradingSubmission:
    name: str
    test_suites: List[GradingTestSuite]


@dataclass_json
@dataclass
class Gradings:
    name: str
    submissions: List[GradingSubmission]


