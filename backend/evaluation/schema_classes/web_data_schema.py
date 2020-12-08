# Auto generated code by script: json_schema_to_class.py
from dataclasses import dataclass
from typing import List, Optional

from dataclasses_json import dataclass_json

__all__ = ["WebDataSubmission", "WebDataTask", "WebDataSubTask", "WebData", "FailedTaskCount", "CodeSnippet"]


@dataclass_json
@dataclass
class FailedTaskCount:
    name: str
    count: int


@dataclass_json
@dataclass
class CodeSnippet:
    class_name: str
    name: str
    code: str
    code_status: str


@dataclass_json
@dataclass
class WebDataSubTask:
    name: str
    description: str
    max_points: int
    auto_points: int
    passed: bool
    code_snippets: List[CodeSnippet]
    error_message: Optional[str] = ""


@dataclass_json
@dataclass
class WebDataTask:
    name: str
    class_name: str
    num_tests: int
    num_passed: int
    num_failed: int
    max_points: int
    sub_tasks: List[WebDataSubTask]


@dataclass_json
@dataclass
class WebDataSubmission:
    name: str
    max_points: int
    tasks: WebDataTask
    error_message: Optional[str] = ""
    failed_task: Optional[str] = ""


@dataclass_json
@dataclass
class WebData:
    num_submissions: int
    num_passed: int
    failed_tasks: List[FailedTaskCount]
    submissions: List[WebDataSubmission]
