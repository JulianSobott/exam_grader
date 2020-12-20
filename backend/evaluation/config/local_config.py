from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dataclasses_json import dataclass_json


@dataclass
class MongoDbConfig:
    run_local: bool = False
    url: str = "mongodb://localhost:27017/"


@dataclass_json
@dataclass
class LocalConfig:
    """Stores the data of the local config file.
    When a new attribute is added, it must also be added in the `get_local_config()` function
    """
    submissions_folder: Path
    reference_project: Path  # path to folder with gradle project in it
    canvas_token: str = None
    mongodb: MongoDbConfig = field(default_factory=MongoDbConfig)


cfg: LocalConfig = None


def get_local_config(reload=False) -> LocalConfig:
    global cfg
    if not cfg or reload:
        root_path = Path(__file__).parents[3]
        config_path = root_path.joinpath("local.config.yaml")
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
            temp: LocalConfig = LocalConfig.from_dict(data)
            temp.submissions_folder = Path(temp.submissions_folder)
            temp.reference_project = Path(temp.reference_project)
            cfg = temp
    return cfg
