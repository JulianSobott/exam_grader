from dataclasses import dataclass
from enum import Enum
from typing import List


class CodeType(Enum):
    METHOD = 0
    CONSTRUCTOR = 1
    ATTRIBUTES = 2
    CLASS = 3


@dataclass
class CodeSnippet:
    codeType: CodeType
    name: str = None


@dataclass
class SubTask:
    name: str
    description: str
    points: float
    code_snippets: List[CodeSnippet]


@dataclass
class Task:
    name: str
    class_name: str
    sub_tasks: List[SubTask]


@dataclass
class Exam:
    tasks: List[Task]


@dataclass
class GlobalConfig:
    exam: Exam
    course_id: str
    quiz_id: str


cfg: GlobalConfig = None


def get_global_config():
    global cfg
    if not cfg:
        cfg = GlobalConfig(None, "2395", "7542")  # TODO load from file
    return cfg
