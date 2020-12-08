import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Tuple, Optional

from common import logger, submission_folder, error
from get_code import get_method_code, get_attributes_code, get_class_header_code, get_constructor_code
from schema_classes import Submission
from schema_classes.web_data_schema import CodeSnippet
from test_code_mapping import *
from test_results import load_test_results

reports_folder = Path(__file__).parent.parent.parent.joinpath("build/test-results")


def create_report(searched_submission_names: list = None) -> Tuple[Optional[dict], error]:
    test_results, err = load_test_results()
    if err:
        return None, "Could not load test results"
    test_results.submissions.sort(key=lambda s: s.name)
    report = {
        "time_end": test_results.time_end,
        "num_submissions": len(test_results.submissions),
        "num_passed": 0,
        "submissions": [],
        "failed_tasks": {}
    }
    for submission in test_results.submissions:
        if searched_submission_names is None or submission.name in searched_submission_names:
            submission, err = create_submission_report(submission)
            if err:
                logger.error(err)
            else:
                report["submissions"].append(submission)
                if submission["passed"]:
                    report["num_passed"] += 1
                else:
                    if not report["failed_tasks"].get(submission["failed_task"]):
                        report["failed_tasks"][submission["failed_task"]] = 0
                    report["failed_tasks"][submission["failed_task"]] += 1
    return report, ""


def create_submission_report_for_hopeless_case(submission_data: Submission):
    pre_testcases_map = {}
    pre_testsuite_names = set()
    for testcase_name, config in test_code_mapping.items():
        testsuite_name = config[0][0]
        pre_testsuite_names.add(testsuite_name)
        if not pre_testcases_map.get(testsuite_name):
            pre_testcases_map[testsuite_name] = []
        pre_testcases_map[testsuite_name].append(testcase_name)

    sub_max_points = 0
    testsuites = [None, None, None]     # TODO: adjust
    testsuite_names = pre_testsuite_names
    for testsuite_name in testsuite_names:
        testcases = []
        testcase_names = pre_testcases_map[testsuite_name]
        max_points = 0
        for testcase_name in testcase_names:
            code_snippets = code_snippets_for_testcase(submission_data.name, testcase_name)
            testcase = {
                "name": testcase_name,
                "max_points": test_points_mapping[testcase_name],
                "auto_points": 0,
                "code_snippets": code_snippets,
                "passed": False,
                "error_message": "not testes",
                "stack": "",
                "submission_name": submission_data.name,
                "testsuite_name": testsuite_name,
            }
            testcases.append(testcase)
            max_points += testcase["max_points"]

        num_tests = len(testcases)
        test_suite = {
            "name": testsuite_name,
            "passed": False,
            "num_tests": num_tests,
            "num_passed": 0,
            "num_failed": num_tests,
            "testcases": testcases,
            "submission_name": submission_data.name,
            "max_points": max_points,
        }
        testsuites[test_suite_order_map[testsuite_name]] = test_suite
        sub_max_points += max_points
    submission = {
        "name": submission_data.name,
        "passed": False,
        "failed_task": submission_data.failed_task,
        "error_message": submission_data.error_message,
        "testsuites": testsuites,
        "max_points": sub_max_points,
    }
    return submission


def create_submission_report(submission_data: Submission) -> Tuple[Optional[dict], error]:
    submission = {
        "name": submission_data.name,
        "passed": False if submission_data.failed_task else True,
        "failed_task": submission_data.failed_task,
        "error_message": submission_data.error_message,
        "testsuites": [None, None, None], # TODO: adjust
        "max_points": 0,
    }

    submission_path = reports_folder.joinpath(submission_data.name).joinpath("test")
    if not submission_path.exists():
        return create_submission_report_for_hopeless_case(submission_data), ""

    for testsuite_file in submission_path.iterdir():
        if testsuite_file.is_file():
            test_suite_tree = ET.parse(testsuite_file)
            testsuite = create_testsuite(test_suite_tree, submission["name"])
            submission["testsuites"][test_suite_order_map[testsuite["name"]]] = testsuite
            submission["max_points"] += testsuite["max_points"]

    for suite in submission["testsuites"]:
        for case in suite["testcases"]:
            case["code_snippets"] = code_snippets_for_testcase(submission["name"], case["name"])
    return submission, ""


def code_snippets_for_testcase(submission_name: str, testcase_name: str):
    code_folder = submission_folder.joinpath(submission_name)
    mapping = test_code_mapping[testcase_name]
    code_snippets = []
    for code_attributes in mapping:
        class_name = code_attributes[0]
        code_type = code_attributes[1]
        if code_type == METHOD:
            method_name = code_attributes[2]
        else:
            method_name = "Should not happen: Error"
        d = {
            METHOD: {
                "function": lambda: get_method_code(code_folder, class_name, method_name),
                "name": method_name,
            },
            ATTRIBUTES: {
                "function": lambda: get_attributes_code(code_folder, class_name),
                "name": "Attributes"
            },
            CLASS: {
                "function": lambda: get_class_header_code(code_folder, class_name),
                "name": "Class declaration"
            },
            CONSTRUCTOR: {
                "function": lambda: get_constructor_code(code_folder, class_name),
                "name": "Constructor"
            }
        }
        code, code_status = d[code_type]["function"]()
        code_snippet = CodeSnippet(class_name, d[code_type]["name"], code, code_status.value)
        code_snippets.append(code_snippet)
    return code_snippets


def create_testsuite(testsuite_tree: ET, submission_name: str) -> dict:
    t = testsuite_tree.getroot().attrib
    test_suite = {
        "name": t.get("name").replace("Test", ""),
        "passed": True,
        "num_tests": t.get("tests"),
        "num_passed": int(t.get("tests")) - int(t.get("failures")),
        "num_failed": t.get("failures"),
        "testcases": [],
        "submission_name": submission_name,
        "max_points": 0,
    }
    test_cases_tree = testsuite_tree.findall("testcase")
    for test_case_tree in test_cases_tree:
        testcase = create_testcase(test_case_tree)
        testcase["testsuite_name"] = test_suite["name"]
        testcase["submission_name"] = submission_name
        if not testcase["passed"]:
            test_suite["passed"] = False
        test_suite["testcases"].append(testcase)
        test_suite["max_points"] += testcase["max_points"]
    return test_suite


def create_testcase(testcase_tree: ET) -> dict:
    t = testcase_tree.attrib
    name = t.get("name")[:-2]    # cut ...() parenthesis
    testcase = {
        "name": name,
        "max_points": test_points_mapping[name],
        "auto_points": test_points_mapping[name],
    }
    failure = testcase_tree.find("failure")
    if failure is not None:
        testcase["passed"] = False
        testcase["auto_points"] = 0
        testcase["error_message"] = failure.attrib.get("message")
        start = failure.text.find(testcase["name"])
        line_nr = failure.text.count("\n", 0, start)
        shortened = list(map(str.strip, failure.text.split("\n")))[line_nr-5:line_nr+5]
        testcase["stack"] = "...\n" + "\n".join(shortened) + "\n..."
    else:
        testcase["passed"] = True
    return testcase
