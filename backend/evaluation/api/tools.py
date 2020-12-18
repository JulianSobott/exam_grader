from pathlib import Path

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
        failures, err = task_extract_zip(zip_path)
        if err:
            pass  # TODO
        return PreparePOST200Response(failures)


class TestFilesRequest(TestFilesRequestBase):

    def handle_get(self, data: "TestFilesGETRequest") -> "TestFilesGETResponse":
        failures, err = get_file_failures()
        if err:
            pass  # TODO
        return TestFilesGET200Response(failures)


class RenameAndFillRequest(RenameAndFillRequestBase):

    def handle_post(self, data: RenameAndFillPOSTRequest) -> "RenameAndFillPOSTResponse":
        rename_files(data.files)
        fill_missing_files()
        failures, err = get_file_failures()
        if err:
            pass  # TODO
        return RenameAndFillPOST200Response(failures)
