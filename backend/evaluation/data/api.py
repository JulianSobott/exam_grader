from config.exam_config import get_exam_config
from data.internal import exams, submissions
from data.schemas import Exam, Submission, Student, Task, Subtask, Testcases
from schema_classes.grading_schema import SubmissionData, Identifier, TaskData, SubTaskData, StepFailed
from schema_classes.overview_schema import OverviewGET200Response, SubmissionOverview, ExamPoints, GradingStatus
from utils.p_types import error

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
            temp = SubmissionOverview(sub.student.name, False, None, bookmarked, sub.status_grading)
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


def submission_data(submission_name: str) -> SubmissionData:
    """db Submission to frontend submission"""
    res = submissions().find_one({"full_name": submission_name, "exam_name": exam_name})
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
                SubTaskData(st.name, st.description, st.points, st.max_points, st.bookmarked, st.code_snippets))
        tasks.append(
            TaskData(t.name, task_points, task_max_points, t.bookmarked, subtasks))
    return SubmissionData(sub.student.name, sub.student.student_number, num_correct, num_subtasks,
                          points_sub, max_points_sub, tasks, sub.step_failed)


def set_points(identifier: Identifier) -> error:
    pass


def set_comment(identifier: Identifier) -> error:
    pass


def set_bookmark(identifier: Identifier) -> error:
    pass


def set_status(identifier: Identifier) -> error:
    pass


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
