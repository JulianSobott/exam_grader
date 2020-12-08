from dataclasses import dataclass
from pathlib import Path


@dataclass
class LocalConfig:
    raw_submissions_path: Path
    structured_submissions_path: Path
    reference_project: Path  # path to folder with gradle project in it
