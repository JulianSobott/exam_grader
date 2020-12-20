from enum import Enum
from pathlib import Path
from typing import Tuple

import regex

from gittools import get_class_at_state, CommitState
from utils.project_logging import get_logger

logger = get_logger("GetCode")


class CodeStatus(Enum):
    ORIGINAL = "original"
    MODIFIED = "modified"
    NOT_FOUND = "not found"


def beautify_code(func):
    def inner(*args, **kwargs):
        code, found = func(*args, **kwargs)
        if found:
            code = code.strip()
        return code, found

    return inner


re_class_header = regex.compile(r"\w*\s*class \w*.*", regex.V1)
re_attributes = regex.compile(r"(private|public|protected)\s*(static)?\s*\w+(\[\])?\s+\w+\s*(=\s*.*)?;")


@beautify_code
def get_class_header_code(submission: Path, class_name: str) -> Tuple[str, CodeStatus]:
    for code, code_status in iter_code_commits(submission, class_name):

        match = regex.search(re_class_header, code)
        if match is not None:
            return match.group(0), code_status
    logger.debug(f"[get_code] not found: {submission.name}/{class_name} header in any commit")
    return "", CodeStatus.NOT_FOUND


@beautify_code
def get_method_code(submission: Path, class_name: str, method_name: str) -> Tuple[str, CodeStatus]:
    re_method = regex.compile(r".*" + method_name + r"\s*\([^)]*\)\s*(\{(?:[^}{]+|(?1))*+\})", regex.V1)
    for code, code_status in iter_code_commits(submission, class_name):
        match = regex.search(re_method, code)
        if match is not None:
            return match.group(0), code_status
    logger.debug(f"[get_code] not found: {submission.name}/{class_name}/{method_name} in any commit")
    return "", CodeStatus.NOT_FOUND


@beautify_code
def get_attributes_code(submission: Path, class_name: str) -> Tuple[str, CodeStatus]:
    for code, code_status in iter_code_commits(submission, class_name):
        found_code = ""
        for match in regex.finditer(re_attributes, code):
            m = match.group(0)
            if "return " not in m:
                found_code += m + "\n"
        if found_code:
            return found_code, code_status
    logger.debug(f"[get_code] not found: {submission.name}/{class_name} attributes in any commit")
    return "", CodeStatus.NOT_FOUND


@beautify_code
def get_constructor_code(submission: Path, class_name: str) -> Tuple[str, CodeStatus]:
    re_constructors = regex.compile(r"\w*\s*" + class_name + r"\s*\([^)]*\)\s*(\{(?:[^}{]+|(?1))*+\})", regex.V1)
    for code, code_status in iter_code_commits(submission, class_name):
        found_code = ""
        for match in regex.finditer(re_constructors, code):
            m = match.group(0)
            found_code += m + "\n"
        if found_code:
            return found_code, code_status
    logger.debug(f"[get_code] not found: {submission.name}/{class_name} constructor in any commit")
    return "", CodeStatus.NOT_FOUND


@beautify_code
def get_full_class(submission: Path, class_name: str) -> Tuple[str, CodeStatus]:
    for code, code_status in iter_code_commits(submission, class_name):
        return code, code_status
    return "", CodeStatus.NOT_FOUND


def iter_code_commits(submission: Path, class_name: str):
    submission_name = submission.name
    # TODO: improve mapping
    commit_state_2_code_status = {
        CommitState.INITIAL: CodeStatus.ORIGINAL,
        CommitState.NAMING: CodeStatus.ORIGINAL,
        CommitState.FILL: CodeStatus.MODIFIED,
        CommitState.FIXES: CodeStatus.MODIFIED
    }
    for commit_state in [CommitState.INITIAL, CommitState.NAMING, CommitState.FILL, CommitState.FIXES]:
        code, err = get_class_at_state(submission_name, class_name, commit_state)
        if err:
            continue
        else:
            yield code, commit_state_2_code_status[commit_state]
