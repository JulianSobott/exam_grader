from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

from schema_classes.grading_schema import StepFailed, Testcase
from schema_classes.overview_schema import GradingStatus


@dataclass_json
@dataclass
class Student:
    name: str
    student_number: str


@dataclass_json
@dataclass
class Exam:
    name: str
    submissions: List["Submission"]


@dataclass_json
@dataclass
class Submission:
    full_name: str  # unique. name of the folder e.g. max_muster-1234
    exam_name: str  # for reference
    student: Student
    tasks: List["Task"]
    bookmarked: bool
    status_grading: GradingStatus
    step_failed: Optional[StepFailed] = None
    compile_error_code: Optional[str] = None


@dataclass_json
@dataclass
class Task:
    name: str
    max_points: float
    subtasks: List["Subtask"]
    bookmarked: bool
    description: Optional[str] = None


@dataclass_json
@dataclass
class Testcases:
    testcases: List[Testcase]


@dataclass_json
@dataclass
class Subtask:
    name: str
    description: str
    max_points: float
    points: float
    bookmarked: bool
    code_snippets: Optional[List["CodeSnippet"]] = None  # only optional to make loading from db easier
    testcases: Optional[Testcases] = None


@dataclass_json
@dataclass
class CodeSnippet:
    name: str
    class_name: str
    found: bool
    code: Optional[str] = None
