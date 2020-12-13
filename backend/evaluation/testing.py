import os
import re
import subprocess
from dataclasses import dataclass
from typing import Tuple, NewType, Optional, List

from dataclasses_json import dataclass_json

from common import structured_submissions, iter_submissions_folders, submission_results_folder
from config.local_config import get_local_config
from utils.p_types import error, new_error
from utils.project_logging import get_logger

logger = get_logger(__name__)

Task = NewType("Task", str)
TASK_JAVA = Task("compileJava")
TASK_KOTLIN = Task("compileTestKotlin")
TASK_TEST = Task("test")

file_id = "0"  # automatically set if needed
test_report_file = submission_results_folder.joinpath(f"test_results_{file_id}.json")


@dataclass_json
@dataclass
class SubmissionTestResult:
    name: str
    passed: bool
    error_message: Optional[str] = ""
    failed_task: Optional[str] = ""


@dataclass_json
@dataclass
class TestResults:
    submissions: List[SubmissionTestResult]


def run_tests_for_all():
    submissions = []
    for abs_path_submission in iter_submissions_folders():
        sub = run_test_for_submission(abs_path_submission.name)
        submissions.append(sub)
    results = TestResults(submissions)
    save_test_results(results)


def run_tests_for_submissions(submissions: List[str]):
    prev_results, err = load_test_results()
    if err:
        logger.warning(f"{err}")
        prev_results = TestResults([])
    for abs_path_submission in iter_submissions_folders():
        submission = abs_path_submission.name
        if submission in submissions:
            sub_res = run_test_for_submission(abs_path_submission.name)

            # replace old submission
            for i, old_submission in enumerate(prev_results.submissions):
                if old_submission.name == submission:
                    prev_results.submissions[i] = sub_res
                    break
            else:   # not found
                prev_results.submissions.append(sub_res)
    save_test_results(prev_results)


def run_test_for_submission(submission: str):
    logger.info(f"[{submission}] testing: {submission} ...")
    res = run_tests(submission)
    ret, failed = failed_task(res, submission)
    return SubmissionTestResult(submission, not failed, ret[1] if failed else None, ret[0] if failed else None)


def run_tests(submission_name: str) -> subprocess.CompletedProcess:
    gradle_wrapper = "./gradlew" if os.name == "posix" else "gradlew.bat"
    command = f"{gradle_wrapper} -Psubmission=\"{submission_name}\" -PsubmissionFolder=\"{structured_submissions}\" test"
    try:
        res = subprocess.run(
            command,
            cwd=get_local_config().reference_project,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
            shell=True
        )
    except subprocess.TimeoutExpired as e:
        res = subprocess.CompletedProcess(command, 27, stdout=e.stdout, stderr=e.stderr)
    return res


def extract_error_message(output: str, task: str, stderr_content: str) -> Tuple[str, bool]:
    failure1 = re.findall(f"> Task :{task}\\s+(?P<failure>.*)\\s*> Task :test FAILED", output, flags=re.S)
    failure2 = re.findall(f"> Task :{task} FAILED\\s*(?P<failure>.*)\\s*Deprecated", output, flags=re.S)
    if failure1 and failure1[0]:
        if failure2 and failure2[0]:
            if len(failure1[0]) > len(failure2[0]):
                failure = failure1[0]
            else:
                failure = failure2[0]
        else:
            failure = failure1[0]
    else:
        if failure2 and failure2[0]:
            failure = failure2[0]
        else:
            err = re.findall(f"(?P<failure>.*)FAILURE", stderr_content, flags=re.S)
            if err:
                failure = err[0]
            else:
                failure = ""
    return failure.strip(), failure != ""


def failed_task(res: subprocess.CompletedProcess, submission: str) -> Tuple[Optional[Tuple[Task, str]], bool]:
    try:
        err_output = str(res.stderr, encoding='utf8')
    except:
        err_output = str(res.stderr)
    logger.debug(f"Error message: {err_output}")
    failed_tasks = re.findall(r"> Task :(?P<task_name>\S*) FAILED", str(res.stdout, encoding="utf8"))
    if len(failed_tasks) != 0:
        task = failed_tasks[0]
        logger.info(f"[{submission}] failed Task: {task}")
        output = str(res.stdout, encoding='utf8')
        err_msg, found = extract_error_message(output, task, err_output)
        if found:
            logger.debug(f"[{submission}] Error message:\n{err_msg}")
        else:
            logger.debug(f"[{submission}] BEGIN_FULL_OUTPUT:\n{output}\nEND_FULL_OUTPUT")
            err_msg = output
        return (Task(task), err_msg), True
    else:
        logger.info(f"[{submission}] Passed all tests")
        return None, False


def save_test_results(results: TestResults) -> None:
    test_report_file.parent.mkdir(parents=True, exist_ok=True)
    with open(test_report_file, "w") as f:
        f.write(results.to_json())


def load_test_results() -> Tuple[Optional[TestResults], error]:
    try:
        with open(test_report_file, "r") as f:
            return TestResults.from_json(f.read()), None
    except FileNotFoundError as e:
        return None, new_error(str(e))
    except Exception as e:
        return None, new_error(str(e))


if __name__ == '__main__':
    run_tests_for_all()
