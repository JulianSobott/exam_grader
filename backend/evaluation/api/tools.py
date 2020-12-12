import zipfile
from pathlib import Path

from common import raw_submissions
from schema_classes.tools_schema import *
from tool_api import *


class PrepareRequest(PrepareRequestBase):

    def handle_post(self, data: PreparePOSTRequest) -> "PreparePOSTResponse":
        zip_path = Path(data.zip_url)
        # since canvas api doesnt provide a simple way to download the zip we must manually download it and provide the
        # local path to the zip file

        if not zip_path.exists():
            return PreparePOST400Response(
                PrepareError.FILE_NOT_FOUND,
                f"Zip file not found. Make sure you have read access to this path: {zip_path}"
            )

        with zipfile.ZipFile(zip_path, "r") as f:
            f.extractall(raw_submissions)

        err = copy_raw_to_structured()
        if err:
            pass  # TODO
        failures = get_file_failures()
        return PreparePOST200Response(failures)


class TestFilesRequest(TestFilesRequestBase):

    def get(self, data: TestFilesGETRequest) -> "TestFilesGETResponse":
        failures = get_file_failures()
        return TestFilesGET200Response(failures)


class RenameAndFillRequest(RenameAndFillRequestBase):

    def post(self, data: RenameAndFillPOSTRequest) -> "RenameAndFillPOSTResponse":
        rename_files(data.files)
        fill_missing_files()
        failures = get_file_failures()
        return RenameAndFillPOST200Response(failures)
