import re
from dataclasses import dataclass
from typing import List, Optional

import requests

from config.exam_config import get_exam_config_else_raise
from config.local_config import get_local_config
from utils.p_types import error, new_error


@dataclass
class QuestionGrading:
    question_id: str
    score: Optional[float]  # None for no changes
    comment: Optional[str]  # None for no changes


def update_scores_comments(submission_id: str, question_gradings: List[QuestionGrading], fudge_points: float = None) \
        -> error:
    data = {
        "quiz_submissions": [
            {
                "attempt": 1,  # For now all quizzes have only one attempt
                "fudged_points": fudge_points,
                "questions": {}
            }
        ]
    }
    for grade in question_gradings:
        data["quiz_submissions"][0]["questions"][grade.question_id] = {
            "score": grade.score,
            "comment": grade.comment
        }
    res = api_call(f"/submissions/{submission_id}", data, requests.put)
    if res.status_code == 200:
        return None
    else:
        return new_error(res.text)


def get_student_ids():
    mapping = {}
    next_url = None
    x = re.compile(r"<([^>]+)>")
    local_cfg = get_local_config()

    while True:
        if next_url is None:
            res = api_call(f"/submissions?per_page=10", None, requests.get)
        else:
            res = requests.get(next_url, headers={"Authorization": f"Bearer {local_cfg.canvas_token}"})

        d = res.json()
        for sub in d["quiz_submissions"]:
            mapping[str(sub["user_id"])] = str(sub["id"])

        # next page
        links_raw = res.headers["link"]
        links = links_raw.split(",")

        current = x.findall(links[0])
        next_ = x.findall(links[1])
        last = x.findall(links[-1])
        if current[0] == last[0]:
            break
        else:
            next_url = next_[0]
    return mapping


def api_call(uri: str, data: dict, method) -> requests.Response:
    local_cfg = get_local_config()
    exam_cfg = get_exam_config_else_raise()
    return method(f"{exam_cfg.canvas_quiz_url}{uri}", json=data,
                  headers={"Authorization": f"Bearer {local_cfg.canvas_token}"})


if __name__ == '__main__':
    # get_student_ids()
    print(update_scores_comments("55263", [QuestionGrading("105159", 2, "New update (testing the api)")]))
