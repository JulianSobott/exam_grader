from dataclasses import dataclass
from typing import Optional, List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Submission:
    name: str
    time_start: str
    time_end: str
    passed: bool
    error_message: Optional[str] = ""
    failed_task: Optional[str] = ""


@dataclass_json
@dataclass
class Results:
    time_start: str
    submissions: List[Submission]
    time_end: str