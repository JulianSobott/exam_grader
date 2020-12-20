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
    data = {"Name": [], "Punkte": [], "Canvas ID": []}
    for submission in grading.submissions:
        data["Name"].append(submission.submission_name)
        points = [e for e in submission.exam_points if e.exam_name == exam_name][0]
        data["Punkte"].append(points)
        data["Canvas ID"].append(submission.submission_id.replace(f"{submission.submission_name}-", ""))

    df = pd.DataFrame(data)
    df.to_excel(path, index=False)
    logger.info(f"created exel file at: {path.absolute()}")
