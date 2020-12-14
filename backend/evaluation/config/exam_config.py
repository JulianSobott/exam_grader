from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Tuple, Optional

import yaml
from dataclasses_json import dataclass_json

from config.local_config import get_local_config
from utils.p_types import error, new_error


class CodeType(Enum):
    METHOD = "METHOD"
    CONSTRUCTOR = "CONSTRUCTOR"
    ATTRIBUTES = "ATTRIBUTES"
    CLASS_HEADER = "CLASS_HEADER"


@dataclass
class CodeSnippetConfig:
    code_type: CodeType
    name: str = None


@dataclass
class SubTaskConfig:
    description: str
    points: str
    code_snippets: List[CodeSnippetConfig]


@dataclass
class TaskConfig:
    class_name: str
    subtasks: Dict[str, SubTaskConfig]


@dataclass_json
@dataclass
class ExamConfig:
    name: str
    tasks: Dict[str, TaskConfig]


config = None


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
    for t in conf.tasks:
        files.append(f"{t}.java")
    return files, None
