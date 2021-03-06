from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Tuple, Optional

import yaml
from dataclasses_json import dataclass_json

from config.local_config import get_local_config
from static_code_testing.attributes import AttributeTest
from static_code_testing.class_declaration import ClassTest
from static_code_testing.method import MethodTest
from utils.p_types import error, new_error


class CodeType(Enum):
    METHOD = "METHOD"
    CONSTRUCTOR = "CONSTRUCTOR"
    ATTRIBUTES = "ATTRIBUTES"
    CLASS_HEADER = "CLASS_HEADER"
    CLASS = "CLASS"


@dataclass
class CodeSnippetConfig:
    code_type: CodeType
    name: Optional[str] = None


@dataclass
class StaticTests:
    class_header: Optional[ClassTest] = None
    attributes: List[AttributeTest] = field(default_factory=list)
    methods: List[MethodTest] = field(default_factory=list)


@dataclass
class SubTaskConfig:
    description: str
    points: float
    code_snippets: List[CodeSnippetConfig]
    static_tests: Optional[StaticTests] = None
    has_runtime_tests: bool = True


@dataclass
class TaskConfig:
    class_name: str
    subtasks: Dict[str, SubTaskConfig]
    canvas_question_id: str


@dataclass_json
@dataclass
class ExamConfig:
    name: str
    tasks: Dict[str, TaskConfig]
    canvas_quiz_url: str


config = None


def get_exam_config_else_raise() -> ExamConfig:
    conf, err = get_exam_config()
    if err:
        raise ValueError(err)
    return conf


def get_exam_config() -> Tuple[Optional[ExamConfig], error]:
    global config
    if not config:
        path = get_local_config().reference_project.joinpath("exam.config.yaml")
        if not path.exists():
            return None, new_error(f"Path not found: {path}")
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            try:
                config = ExamConfig.from_dict(data)
                return config, None
            except KeyError as e:
                return None, new_error(f"Wrong formatted config: {e}")
    return config, None


def get_required_files() -> Tuple[Optional[List[str]], error]:
    conf, err = get_exam_config()
    if err:
        return None, err
    files = []
    for t in conf.tasks.values():
        files.append(f"{t.class_name}.java")
    return files, None
