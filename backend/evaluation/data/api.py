from typing import Optional, Tuple

from config.exam_config import get_exam_config, get_exam_config_else_raise
from data.internal import exams, submissions
from data.schemas import Exam, Submission, Student, Task, Subtask, Testcases
from schema_classes.grading_schema import SubmissionData, Identifier, TaskData, SubTaskData, StepFailed, \
    SetErrorType
from schema_classes.overview_schema import OverviewGET200Response, SubmissionOverview, ExamPoints, GradingStatus
from utils.p_types import error, new_error

OverviewData = OverviewGET200Response
exam_name: str = None


def preprocess_constant_fields():
    """This function must be called before any other functions of this file are called.
    Initializes some global variables that are used frequently used and never change
    """
    global exam_name
    config, err = get_exam_config()
    if err:
        raise ValueError(err)
    exam_name = config.name


preprocess_constant_fields()


def create_exam_if_not_exist():
    """Adds the exam if it does not exist, otherwise do nothing"""
    exams().update_one({"name": exam_name}, {"$setOnInsert": Exam(exam_name, []).to_dict()}, upsert=True)


def insert_submission(submission: Submission):
    data = submission.to_dict()
    data["status_grading"] = data["status_grading"].value  # enum to string (mongodb can't handle enums)
    submissions().insert_one(data)


def overview_data() -> OverviewData:
    res = submissions().aggregate([
        {
            "$project": {"tasks.subtasks.code_snippets": 0}
        }
    ])

    submissions_intermediate_data = {}

    for r in res:
        sub: Submission = Submission.from_dict(r)
        bookmarked = False
        points = 0
        max_points = 0
        for t in sub.tasks:
            if t.bookmarked:
                bookmarked = True
            for st in t.subtasks:
                if st.bookmarked:
                    bookmarked = True
                points += st.points
                max_points += st.max_points
        if sub.student.name not in submissions_intermediate_data:
            submissions_intermediate_data[sub.student.name] = {"overview": None, "points": []}
        if sub.exam_name == exam_name:
            temp = SubmissionOverview(sub.student.name, sub.full_name, False, None, bookmarked, sub.status_grading)
            submissions_intermediate_data[sub.student.name]["overview"] = temp
        submissions_intermediate_data[sub.student.name]["points"].append(ExamPoints(sub.exam_name, points, max_points))

    overview_submissions = []
    num_passed = 0
    for temp in submissions_intermediate_data.values():
        so: SubmissionOverview = temp["overview"]
        so.exam_points = temp["points"]
        so.reached_min_points = sum(x.points for x in so.exam_points) >= 50
        num_passed += so.reached_min_points
        overview_submissions.append(so)
    return OverviewGET200Response(exam_name, len(overview_submissions), num_passed, overview_submissions)


def submission_data(submission_name: str) -> Tuple[Optional[SubmissionData], error]:
    """db Submission to frontend submission"""
    res = submissions().find_one({"full_name": submission_name, "exam_name": exam_name})
    if not res:
        return None, new_error(f"Submission in exam not found: '{submission_name}' - '{exam_name}'", error_code=404)
    sub: Submission = Submission.from_dict(res)
    num_correct = 0
    num_subtasks = 0
    points_sub = 0
    max_points_sub = 0
    tasks = []
    for t in sub.tasks:
        task_points = 0
        task_max_points = 0
        subtasks = []
        for st in t.subtasks:
            num_correct += st.points == st.max_points
            num_subtasks += 1
            points_sub += st.points
            max_points_sub += st.max_points
            task_points += st.points
            task_max_points += st.max_points
            subtasks.append(
                SubTaskData(st.name, st.description, st.points, st.max_points, st.bookmarked, st.code_snippets,
                            st.testcases))
        tasks.append(
            TaskData(t.name, task_points, task_max_points, t.bookmarked, t.full_code, subtasks))
    return SubmissionData(sub.student.name, sub.student.student_number, num_correct, num_subtasks,
                          points_sub, max_points_sub, tasks, sub.step_failed), None


RESOURCE_SUBMISSION = 1 << 1
RESOURCE_TASK = 1 << 2
RESOURCE_SUBTASK = 1 << 3


def set_points(identifier: Identifier, points: float) -> Optional[SetErrorType]:
    return _set(identifier, "points", points, RESOURCE_SUBTASK)


def set_comment(identifier: Identifier, comment: str) -> Optional[SetErrorType]:
    return _set(identifier, "comment", comment, RESOURCE_SUBTASK | RESOURCE_TASK)


def set_bookmark(identifier: Identifier, bookmarked: bool) -> Optional[SetErrorType]:
    return _set(identifier, "bookmarked", bookmarked, RESOURCE_SUBTASK | RESOURCE_TASK | RESOURCE_SUBMISSION)


def set_status(identifier: Identifier, status: GradingStatus) -> Optional[SetErrorType]:
    return _set(identifier, "status_grading", status.value, RESOURCE_SUBMISSION)


def update_test_results(submission_name: str, error_message: str, step_failed: StepFailed):
    submissions().update_one({"exam_name": exam_name, "full_name": submission_name},
                             {
                                 "$set": {
                                     "step_failed": step_failed.value,
                                     "compile_error_code": error_message
                                 },
                             })


def set_testcases(submission_name, task_name: str, subtask_name: str, testcases: Testcases):
    submissions().update_one({"exam_name": exam_name, "full_name": submission_name},
                             {"$set": {"tasks.$[i].subtasks.$[j].testcases": testcases.to_dict()["testcases"]}},
                             array_filters=[{"i.name": task_name}, {"j.name": subtask_name}]
                             )
    if all(t.passed for t in testcases.testcases):
        cfg = get_exam_config_else_raise()
        max_points = cfg.tasks[task_name].subtasks[subtask_name].points
        set_points(Identifier([submission_name, task_name, subtask_name]), max_points)


SUBMISSION_IDX = 0
TASK_IDX = 1
SUBTASK_IDX = 2


def _build_identifier_parts(identifier: Identifier) -> Tuple[str, list]:
    ret = ""
    array_filters = []
    if len(identifier.elements) >= 2:
        ret += "tasks.$[i]."
        array_filters.append({"i.name": identifier.elements[TASK_IDX]})
    if len(identifier.elements) >= 3:
        ret += "subtasks.$[j]."
        array_filters.append({"j.name": identifier.elements[SUBTASK_IDX]})
    return ret, array_filters


def _set(identifier: Identifier, key: str, value, allowed_resources: int) -> Optional[SetErrorType]:
    if not ((1 << len(identifier.elements)) & allowed_resources):
        return SetErrorType.RESOURCE_NOT_ALLOWED_FOR_IDENTIFIER
    set_uri, array_filters = _build_identifier_parts(identifier)
    res = submissions().update_one({"exam_name": exam_name, "full_name": identifier.elements[SUBMISSION_IDX]},
                                   {"$set": {f"{set_uri}{key}": value}},
                                   array_filters=array_filters
                                   )
    assert res.matched_count < 2, f"Duplicated element in DB! {identifier.elements}"
    if res.matched_count != 1:
        return SetErrorType.NOT_FOUND
    return None


def debug_reset_all_data():
    exams().delete_many({})
    create_exam_if_not_exist()
    submissions().delete_many({})


if __name__ == '__main__':
    # Testing
    debug_reset_all_data()

    exam_1 = "Exam1"

    submissions().insert_many([
        Submission("P1", exam_name, Student("P1", "12345"),
                   [
                       Task("myTAsk", 10, [Subtask("sub", "a description", 34, 20, True, [])], False),
                       Task("myTAsk2", 20, [Subtask("sub2", "a descri2ption", 5, 4, False, [])], False)
                   ], False, GradingStatus.ACTIVE.value).to_dict(),
        Submission("P1", exam_1, Student("P1", "12345"),
                   [
                       Task("myTAsk", 10, [Subtask("sub", "a description", 5, 4, True, [])], False),
                       Task("myTAsk2", 20, [Subtask("sub2", "a descri2ption", 34, 34, False, [])], False)
                   ], False, GradingStatus.ACTIVE.value).to_dict(),
        Submission("P2", exam_name, Student("P2", "12345"),
                   [
                       Task("myTAsk", 10, [Subtask("sub", "a description", 5, 1, True, [])], False),
                       Task("myTAsk2", 20, [Subtask("sub2", "a descri2ption", 5, 1, False, [])], False)
                   ], False, GradingStatus.ACTIVE.value).to_dict(),
        Submission("P2", exam_1, Student("P2", "12345"),
                   [
                       Task("myTAsk", 10, [Subtask("sub", "a description", 5, 1, True, [])], False),
                       Task("myTAsk2", 20, [Subtask("sub2", "a descri2ption", 5, 1, False, [])], False)
                   ], False, GradingStatus.ACTIVE.value).to_dict(),
    ])
    r = submission_data("P1")
    print(r)
