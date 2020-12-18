import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Tuple, Optional, List, Dict

from dataclasses_json import dataclass_json

from common import structured_submissions, iter_submissions_folders
from config.exam_config import get_exam_config_else_raise
from config.local_config import get_local_config
from data.api import update_test_results, set_testcases
from data.schemas import Testcases
from schema_classes.grading_schema import StepFailed, Testcase
from static_code_testing.attributes import test_attribute
from static_code_testing.class_declaration import test_class
from static_code_testing.method import test_method
from utils.project_logging import get_logger

logger = get_logger(__name__)

task_step_map = {"compileJava": StepFailed.COMPILE_JAVA, "compileTestKotlin": StepFailed.COMPILE_KOTLIN,
                 "test": StepFailed.TEST}
test_results_folder = get_local_config().reference_project.joinpath("build/test-results")


@dataclass_json
@dataclass
class SubmissionTestResult:
    submission_name: str
    passed: bool
    error_message: Optional[str] = ""
    failed_task: Optional[StepFailed] = None
    static_test_results: Dict[str, Dict[str, List[Testcase]]] = field(default_factory=dict)  # task, subtask


@dataclass_json
@dataclass
class TestResults:
    submissions: List[SubmissionTestResult]


def run_tests_for_all() -> TestResults:
    return run_tests_for_submissions(None)


def run_tests_for_submissions(submissions: Optional[List[str]]) -> TestResults:
    """Run tests fro the specified submissions. If submissions is None, ALL submissions are tested"""
    submissions_results = []
    for abs_path_submission in iter_submissions_folders():
        submission_name = abs_path_submission.name
        if submissions is None or submission_name in submissions:
            sub_res = run_test_for_submission(submission_name)
            submissions_results.append(sub_res)
    results = TestResults(submissions_results)
    save_test_results(results)
    return results


def run_test_for_submission(submission_name: str):
    shutil.rmtree(test_results_folder.joinpath(submission_name), ignore_errors=True)
    logger.info(f"[{submission_name}] testing: {submission_name} ...")
    res = run_tests(submission_name)
    ret, failed = failed_task(res, submission_name)
    static_results = run_static_tests(submission_name)
    return SubmissionTestResult(submission_name, not failed, ret[1] if failed else None, ret[0] if failed else None,
                                static_results)


def run_tests(submission_name: str) -> subprocess.CompletedProcess:
    gradle_wrapper = "./gradlew" if os.name == "posix" else "gradlew.bat"
    command = f"{gradle_wrapper} -Psubmission=\"{submission_name}\" -PsubmissionFolder=\"{structured_submissions}\" " \
              f"test"
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


def _testcase_from_failures(name: str, failures: list) -> Testcase:
    if failures:
        return Testcase(name, False, ", ".join(map(str, failures)))
    return Testcase(name, True)


def run_static_tests(submission_name: str) -> Dict[str, Dict[str, List[Testcase]]]:
    cfg = get_exam_config_else_raise()
    results = {}
    for task_name, task in cfg.tasks.items():
        results[task_name] = {}
        with open(structured_submissions.joinpath(submission_name).joinpath(task.class_name + ".java")) as f:
            code = f.read()
        for subtask_name, subtask in task.subtasks.items():
            testcases = []
            tests = subtask.static_tests
            if tests is None:
                continue
            if tests.class_header:
                f = test_class(tests.class_header, code)
                testcases.append(_testcase_from_failures(f"Class {tests.class_header.name}", f))
            for method in tests.methods:
                f = test_method(method, code)
                testcases.append(_testcase_from_failures(f"method: {method.name}", f))
            for attribute in tests.attributes:
                f = test_attribute(attribute, code)
                testcases.append(_testcase_from_failures(f"attribute: {attribute.name}", f))
            results[task_name][subtask_name] = testcases
    return results


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


def failed_task(res: subprocess.CompletedProcess, submission: str) -> Tuple[Optional[Tuple[StepFailed, str]], bool]:
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
        assert task in task_step_map, f"{task} is an unexpected task to fail"
        return (task_step_map[task], err_msg), True
    else:
        logger.info(f"[{submission}] Passed all tests")
        return None, False


def save_test_results(results: TestResults):
    reports_folder = test_results_folder
    for res in results.submissions:
        submission_path = reports_folder.joinpath(res.submission_name).joinpath("test")
        update_test_results(res.submission_name, res.error_message, res.failed_task)

        testcases = {}
        # static
        for task_name, task in res.static_test_results.items():
            testcases[task_name] = {}
            for subtask_name, subtask_testcases in task.items():
                testcases[task_name][subtask_name] = subtask_testcases
        # dynamic
        if submission_path.exists():
            for test_file in submission_path.iterdir():
                if test_file.is_file():
                    testsuite_tree = ET.parse(test_file)
                    testcases_trees = testsuite_tree.findall("testcase")

                    for testcase_tree in testcases_trees:
                        testcase_name = testcase_tree.attrib.get("name")[:-2]  # cut ...() parenthesis
                        identifier = re.findall(r"([0-9]+)\s*(\w+)\).*", testcase_name)
                        assert len(identifier) == 1, f"Wrong testcase name: {testcase_name}"
                        task_name = identifier[0][0]
                        subtask_name = identifier[0][1]
                        failure = testcase_tree.find("./failure")
                        if failure is not None:
                            assertion = parse_assertion_error(failure.attrib.get("message"))
                            testcase = Testcase(testcase_name, False, assertion)
                        else:
                            testcase = Testcase(testcase_name, True)
                        if task_name not in testcases:
                            testcases[task_name] = {}
                        if subtask_name not in testcases[task_name]:
                            testcases[task_name][subtask_name] = []
                        testcases[task_name][subtask_name].append(testcase)

        for task_name, task in testcases.items():
            for subtask_name, subtask_testcases in task.items():
                set_testcases(res.submission_name, task_name, subtask_name, Testcases(subtask_testcases))


def parse_assertion_error(error_text: str):
    match = re.match(r"org.opentest4j.AssertionFailedError: (?P<assertion>.*)",
                     error_text)
    if match:
        return match.group("assertion")
    return error_text


if __name__ == '__main__':
    run_tests_for_all()
