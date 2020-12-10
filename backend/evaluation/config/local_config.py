from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class LocalConfig:
    submissions_folder: Path
    reference_project: Path  # path to folder with gradle project in it


cfg = None


def get_local_config(reload=False) -> LocalConfig:
    global cfg
    if not cfg or reload:
        root_path = Path(__file__).parents[4]
        config_path = root_path.joinpath("local.config.yaml")
        with open(config_path, "r") as f:
            yaml_conf = yaml.load(f)
        cfg = LocalConfig(Path(yaml_conf["submissions_folder"]), Path(yaml_conf["reference_project"]))
    return yaml_conf
