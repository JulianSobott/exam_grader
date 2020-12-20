from typing import List

from canvas.api import QuestionGrading, update_scores_comments
from config.exam_config import get_exam_config_else_raise
from data.api import submission_data, set_points, set_comment, set_bookmark, set_status, overview_data
from grading.create_report import create_comment
from schema_classes.grading_schema import *
from utils.project_logging import get_logger

logger = get_logger(__name__)


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


class SubmitToCanvasRequest(SubmitToCanvasRequestBase):

    def handle_post(self, data: "SubmitToCanvasPOSTRequest") -> "SubmitToCanvasPOSTResponse":
        overview = overview_data()
        errors = []
        for submission in overview.submissions:
            sub_data, err = submission_data(submission.submission_name)
            if err:
                error = f"[{submission.submission_name}] to canvas error: {err}"
                logger.error(error)
                errors.append(error)
            else:
                gradings: List[QuestionGrading] = []
                for task in sub_data.tasks:
                    comment = create_comment(task.sub_tasks)
                    canvas_question_id = get_exam_config_else_raise().tasks[task.name].canvas_question_id
                    grading = QuestionGrading(canvas_question_id, task.points, comment)
                    gradings.append(grading)
                logger.info(f"[{submission.submission_name}] submitting to canvas...")
                err = update_scores_comments(submission.submission_name, gradings)
                if err:
                    error = f"[{submission.submission_name}] submitting failed: {err}"
                    logger.error(error)
                    errors.append(error)
        if errors:
            return SubmitToCanvasPOST500Response("\n".join(errors))
        return SubmitToCanvasPOST200Response()
