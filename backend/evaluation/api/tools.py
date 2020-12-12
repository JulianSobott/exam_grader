import zipfile
from pathlib import Path

from api.utils import api
from common import raw_submissions
from schema_classes.tools_schema import PreparePOSTRequest, Prepare200Response, PrepareResponse, Prepare400Response, \
    PrepareError
from tool_api import *


@api(PreparePOSTRequest)
def prepare(data: PreparePOSTRequest) -> PrepareResponse:
    zip_path = Path(data.zip_url)
    # since canvas api doesnt provide a simple way to download the zip we must manually download it and provide the
    # local path to the zip file

    if not zip_path.exists():
        return PrepareResponse(Prepare400Response(
            PrepareError.FILE_NOT_FOUND,
            f"Zip file not found. Make sure you have read access to this path: {zip_path}"))

    with zipfile.ZipFile(zip_path, "r") as f:
        f.extractall(raw_submissions)

    err = copy_raw_to_structured()
    if err:
        pass
    failures = get_file_failures()
    return PrepareResponse(Prepare200Response(failures))
