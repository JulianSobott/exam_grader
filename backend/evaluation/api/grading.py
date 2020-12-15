from data.api import submission_data
from schema_classes.grading_schema import SubmissionsRequestBase, SubmissionsGETRequest, SubmissionsGETResponse, \
    SubmissionsGET200Response


class SubmissionsRequest(SubmissionsRequestBase):

    def handle_get(self, data: "SubmissionsGETRequest", submission_name: str) -> "SubmissionsGETResponse":
        return SubmissionsGET200Response(submission_data(submission_name))
