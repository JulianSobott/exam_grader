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
    tasks: Dict[str, TaskConfig]


def load_config() -> Tuple[Optional[ExamConfig], error]:
    path = get_local_config().reference_project.joinpath("exam.config.yaml")
    if not path.exists():
        return None, new_error(f"Path not found: {path}")
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        try:
            return ExamConfig.from_dict(data), None
        except KeyError as e:
            return None, new_error(f"Wrong formatted config: {e}")
