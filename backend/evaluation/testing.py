import subprocess
from pathlib import Path
import re
from typing import Tuple, NewType, Optional, List
from datetime import datetime
import os

from common import submission_folder, logger, iter_submissions_folders
from test_results import save_test_results, load_test_results
from schema_classes import Submission, Results

Task = NewType("Task", str)
TASK_JAVA = Task("compileJava")
TASK_KOTLIN = Task("compileTestKotlin")
TASK_TEST = Task("test")


def run_tests_for_all():
    start_time_all = datetime.now()
    submissions = []
    for abs_path_submission in iter_submissions_folders():
        sub = run_test_for_submission(abs_path_submission.name)
        submissions.append(sub)
    end_time_all = datetime.now()
    results = Results(start_time_all.isoformat(), submissions, end_time_all.isoformat())
    save_test_results(results)


def run_tests_for_submissions(submissions: List[str]):
    prev_results, error = load_test_results()
    if error:
        logger.warning(f"[WARNING run_tests] {error}")
        start_time_all = datetime.now()
        prev_results = Results(start_time_all.isoformat(), [], start_time_all.isoformat())
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
    start_time_submission = datetime.now()
    logger.info(f"[{submission}] testing: {submission} ...")
    res = run_tests(submission)
    ret, failed = failed_task(res, submission)
    end_time_submission = datetime.now()
    return Submission(submission, start_time_submission.isoformat(), end_time_submission.isoformat(), not failed,
                      ret[1] if failed else None,
                      ret[0] if failed else None)


def run_tests(submission_name: str) -> subprocess.CompletedProcess:
    gradle_wrapper = "./gradlew" if os.name == "posix" else "gradlew.bat"
    command = f"{gradle_wrapper} -Psubmission=\"{submission_name}\" -PsubmissionFolder=\"{submission_folder}\" test"
    try:
        res = subprocess.run(
            command,
            cwd=Path(__file__).parent.parent.parent,
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
    failed_tasks = re.findall(r"> Task :(?P<task_name>\S*) FAILED", str(res.stdout, encoding="utf8"))
    if len(failed_tasks) != 0:
        task = failed_tasks[0]
        logger.info(f"[{submission}] failed Task: {task}")
        output = str(res.stdout, encoding='utf8')
        try:
            err_output = str(res.stderr, encoding='utf8')
        except:
            err_output = str(res.stderr)
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


if __name__ == '__main__':
    run_tests_for_all()
