import re
from pathlib import Path

import pandas as pd

from utils.project_logging import get_logger

logger = get_logger(__name__)


def create_exel_table(path: Path = Path("OOP_ZK1_PunkteStudierende.xlsx")):
    grading = load_gradings()  # TODO
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
    logger.info(f"created exel file at: {path.absolute()}")
