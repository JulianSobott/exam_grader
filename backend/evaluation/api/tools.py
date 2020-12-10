import zipfile
from pathlib import Path

from api.utils import api
from common import raw_submissions
from preparation import FailureType
from schema_classes.tools_schema import PrepareRequest, PrepareResponse, _HelperClass0
from tool_api import *


@api(PrepareRequest)
def prepare(data: PrepareRequest) -> PrepareResponse:
    zip_path = Path(data.zip_url)
    # since canvas api doesnt provide a simple way to download the zip we must manually download it and provide the
    # local path to the zip file

    with zipfile.ZipFile(zip_path, "r") as f:
        f.extractall(raw_submissions)

    err = copy_raw_to_structured()
    if err:
        pass
    failures = get_file_failures()
    mapping = {FailureType.MISSING: "MISSING", FailureType.WRONG_NAMED: "WRONG_NAMED"}
    transformed = list(map(lambda f: _HelperClass0(
        f.submission_name, f.file_name, mapping[f.failure_type]), failures))
    return PrepareResponse(transformed)
