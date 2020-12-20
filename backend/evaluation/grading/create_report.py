from typing import Tuple, Optional, List

from schema_classes.grading_schema import SubTaskData
from utils.p_types import error


def create_report(submission_names: List[str] = None) -> Tuple[Optional[dict], error]:
    pass  # TODO


def create_comment(subtasks: List[SubTaskData]):
    comment = ""
    for subtask in subtasks:
        if subtask.points == subtask.max_points:
            emoji = "🚀"
        elif subtask.points >= subtask.max_points / 2:
            emoji = "👍"
        elif subtask.points == 0:
            emoji = "😱"
        else:
            emoji = ""
        sub_comment = f"{subtask.name}) {subtask.points}/{subtask.max_points} {emoji}\n"
        if subtask.comment:
            sub_comment += subtask.comment.strip() + "\n"
        sub_comment += "\n"
        comment += sub_comment
    return comment


if __name__ == '__main__':
    print(create_comment([
        Subtask("a", "", 10, 10, False, "THis is awesome"),
        Subtask("b", "", 10, 5, False, ""),
        Subtask("c", "", 10, 0, False, "THis is awesome\nin\nmultiple\nways"),
    ]))
