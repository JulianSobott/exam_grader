from data.api import submission_data, set_points, set_comment, set_bookmark, set_status
from schema_classes.grading_schema import *


class SubmissionsRequest(SubmissionsRequestBase):

    def handle_get(self, data: "SubmissionsGETRequest", submission_name: str) -> "SubmissionsGETResponse":
        sub, err = submission_data(submission_name)
        if err:
            if err.error_code == 404:
                return SubmissionsGET404Response(str(err))
            else:
                return SubmissionsGET500Response(str(err))
        return SubmissionsGET200Response(sub)


class PointsRequest(PointsRequestBase):
    def handle_post(self, data: "PointsPOSTRequest") -> "PointsPOSTResponse":
        err = set_points(data.identifier, data.points)
        if err:
            return PointsPOST400Response(SetError(f"Identifier: {data.identifier}", err))
        return PointsPOST200Response()


class CommentRequest(CommentRequestBase):
    def handle_post(self, data: "CommentPOSTRequest") -> "CommentPOSTResponse":
        err = set_comment(data.identifier, data.comment)
        if err:
            return CommentPOST400Response(SetError(f"Identifier: {data.identifier}", err))
        return CommentPOST200Response()


class BookmarkRequest(BookmarkRequestBase):
    def handle_post(self, data: "BookmarkPOSTRequest") -> "BookmarkPOSTResponse":
        err = set_bookmark(data.identifier, data.bookmarked)
        if err:
            return BookmarkPOST400Response(SetError(f"Identifier: {data.identifier}", err))
        return BookmarkPOST200Response()


class StatusRequest(StatusRequestBase):
    def handle_post(self, data: "StatusPOSTRequest") -> "StatusPOSTResponse":
        err = set_status(data.identifier, data.status)
        if err:
            return StatusPOST400Response(SetError(f"Identifier: {data.identifier}", err))
        return StatusPOST200Response()
