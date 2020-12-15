from data.api import submission_data
from schema_classes.grading_schema import SubmissionsRequestBase, SubmissionsPOSTRequest, SubmissionsPOSTResponse, \
    SubmissionsPOST200Response


class SubmissionsRequest(SubmissionsRequestBase):

    def handle_post(self, data: "SubmissionsPOSTRequest") -> "SubmissionsPOSTResponse":
        return SubmissionsPOST200Response(submission_data(data.submission_name))
