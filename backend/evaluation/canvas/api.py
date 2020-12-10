from dataclasses import dataclass
from typing import List, Optional

import requests

from config.global_config import get_global_config
from config.local_config import get_local_config

base_url = "https://aalen.instructure.com/api/v1/courses/2395"  # TODO: maybe in config/ more general


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
    cfg = get_global_config()
    res = api_call(f"/quizzes/{cfg.quiz_id}/submissions/{submission_id}", data, requests.put)
    print(res)
    print(str(res.content, "utf8"))


def api_call(uri: str, data: dict, method) -> requests.Response:
    cfg = get_local_config()
    return method(f"{base_url}{uri}", json=data, headers={"Authorization": f"Bearer {cfg.canvas_token}"})


if __name__ == '__main__':
    update_scores_comments("48362", [QuestionGrading("105749", 1, "New update")])
