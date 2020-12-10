import zipfile

import requests

from api.utils import api
from config.local_config import get_local_config
from schema_classes.tools_schema import PrepareRequest, PrepareResponse, _HelperClass0


@api(PrepareRequest)
def prepare(data: PrepareRequest) -> PrepareResponse:
    zip_file = requests.get(data.zip_url)
    cfg = get_local_config()
    zip_path = cfg.submissions_folder.joinpath("all.zip")
    with open(zip_path, "w") as f:
        f.write(str(zip_file.content))
    dst_folder = cfg.submissions_folder.joinpath("raw")
    if not dst_folder.exists():
        dst_folder.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as f:
        f.extractall(dst_folder)

    return PrepareResponse([_HelperClass0("sub1", ["1.py", "2.py"], ["Main.java"])])
