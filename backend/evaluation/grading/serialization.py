from pathlib import Path

import pandas as pd

from config.exam_config import get_exam_config_else_raise
from data.api import overview_data
from utils.project_logging import get_logger

logger = get_logger(__name__)


def create_exel_table(path: Path = None):
    exam_name = get_exam_config_else_raise().name
    if path is None:
        path = Path(f"{exam_name}_gradings.xlsx")
    grading = overview_data()
    points = {}
    data = {"Name": [], "Canvas ID": []}
    for submission in grading.submissions:
        if not points:
            points = {e.exam_name: [] for e in submission.exam_points}
            points["sum"] = []
        data["Name"].append(submission.submission_name)
        points_sum = 0
        for e in submission.exam_points:
            points_sum += e.points
            points[e.exam_name].append(e.points)
        points["sum"].append(points_sum)
        data["Canvas ID"].append(submission.submission_id.replace(f"{submission.submission_name}-", ""))

    data = {**data, **points}
    df = pd.DataFrame(data)
    df.to_excel(path, index=False)
    logger.info(f"created exel file at: {path.absolute()}")


if __name__ == '__main__':
    create_exel_table()
