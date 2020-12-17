from dataclasses import dataclass
from typing import List, Optional

import requests

from config.exam_config import get_exam_config_else_raise
from config.local_config import get_local_config


@dataclass
class QuestionGrading:
    question_id: str
    score: Optional[float]  # None for no changes
    comment: Optional[str]  # None for no changes


def update_scores_comments(submission_id: str, question_gradings: List[QuestionGrading], fudge_points: float = None):
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
    print(res)
    print(str(res.content, "utf8"))


def api_call(uri: str, data: dict, method) -> requests.Response:
    local_cfg = get_local_config()
    exam_cfg = get_exam_config_else_raise()
    return method(f"{exam_cfg.canvas_quiz_url}{uri}", json=data,
                  headers={"Authorization": f"Bearer {local_cfg.canvas_token}"})


if __name__ == '__main__':
    update_scores_comments("48362", [QuestionGrading("105749", 1, "New update")])
