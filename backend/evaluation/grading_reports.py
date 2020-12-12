import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import submission_results_folder
from schema_classes.gradings_schema import Gradings, GradingSubmission
from test_code_mapping import test_points_mapping
from utils.project_logging import get_logger

logger = get_logger(__name__)

testcase_comment = """
$NAME
=====
$COMMENT

""".lstrip()


def load_gradings() -> Gradings:
    gradings_file = submission_results_folder.joinpath("gradings.json")
    with open(gradings_file, "r") as f:
        gradings = Gradings.from_json(f.read())
    return gradings


def print_grading_reports():
    gradings = load_gradings()
    for submission in gradings.submissions:
        report = create_submission_report(submission)
        print(report)


def create_submission_report(submission: GradingSubmission):
    data = {
        "points": 0
    }
    for test_suite in submission.test_suites:   # = 1 exercise
        data[test_suite.name] = {
            "points": 0,
            "comment": ""
        }
        for test_case in test_suite.test_cases:
            data[test_suite.name]["points"] += int(test_case.points)
            if test_case.comment:
                comment = test_case.name + "\n" + "=" * len(test_case.name) + "\n" + test_case.comment + "\n\n"
                data[test_suite.name]["comment"] += comment
        data["points"] += data[test_suite.name]["points"]
    return data


def create_exel_table(path: Path = Path("OOP_ZK1_PunkteStudierende.xlsx")):
    grading = load_gradings()
    data = {"MatNr": [], "Punkte": []}
    for submission in grading.submissions:
        submission_points = 0
        for testsuite in submission.test_suites:
            for testcase in testsuite.test_cases:
                submission_points += testcase.points
        mat_nr = "7" + re.findall(r"[0-9]{4}", submission.name)[0]
        data["MatNr"].append(mat_nr)
        data["Punkte"].append(submission_points)

    df = pd.DataFrame(data)
    df.to_excel(path, index=False)
    logger.info(f"[exel] created exel file at: {path.absolute()}")


def create_statistics():
    gradings = load_gradings()
    # points per task
    testcases = {}
    for submission in gradings.submissions:
        for testsuite in submission.test_suites:
            for testcase in testsuite.test_cases:
                if not testcases.get(testcase.name):
                    testcases[testcase.name] = []
                testcases[testcase.name].append(testcase.points)
    i = 1
    testcases_deviation = []
    for name, points in testcases.items():
        p = np.array(points)
        max_points = test_points_mapping[name]
        x = np.sum((max_points - p)/max_points)
        testcases_deviation.append(x)

    x = np.arange(1, len(testcases_deviation) + 1)
    y = np.array(testcases_deviation)

    x_labels = np.array([k for k in test_points_mapping.keys()])
    fix, ax = plt.subplots(1, 1)
    ax.bar(x, y)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation="vertical")
    # plt.bar(x, y)
    plt.title("1 Fehlerrate")
    plt.show()


if __name__ == '__main__':
    create_statistics()
    # create_exel_table()
