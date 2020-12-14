from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class LocalConfig:
    """Stores the data of the local config file.
    When a new attribute is added, it must also be added in the `get_local_config()` function
    """
    submissions_folder: Path
    reference_project: Path  # path to folder with gradle project in it
    canvas_token: str = None
    pymongo_password: str = None


cfg = None


def get_local_config(reload=False) -> LocalConfig:
    global cfg
    if not cfg or reload:
        root_path = Path(__file__).parents[3]
        config_path = root_path.joinpath("local.config.yaml")
        with open(config_path, "r") as f:
            yaml_conf = yaml.safe_load(f)
        cfg = LocalConfig(
            Path(yaml_conf["submissions_folder"]),
            Path(yaml_conf["reference_project"]),
            yaml_conf["canvas_token"],
            yaml_conf["pymongo_password"]
        )
    return cfg
