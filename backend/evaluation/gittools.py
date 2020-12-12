from enum import IntEnum
from typing import Tuple

from git import Repo

from common import structured_submissions
from utils.p_types import error
from utils.project_logging import get_logger

logger = get_logger(__name__)

"""
commits
=======

1. initial (copied all files in dir)
2. naming every file has the correct name
3. fill not existing files
4.+ fixes 
"""


class CommitState(IntEnum):
    INITIAL = 0
    NAMING = 1
    FILL = 2
    FIXES = 3


def _git_add_and_commit(msg: str):
    repo = Repo(structured_submissions)
    repo.git.add(A=True)
    repo.index.commit(msg)
    logger.info(f"[GIT] commit: {repo.commit().message}")


def git_copied_files():
    Repo.init(structured_submissions)
    _git_add_and_commit("Step 1: Copied files to directories")


def git_renamed_files():
    _git_add_and_commit("Step 2: Renamed files")


def git_filled_files():
    _git_add_and_commit("Step 3: Added missing files (files contain minimal implemented class)")


def git_fixed_code():
    _git_add_and_commit("Step 4: Fixed code, so it can be compiled")


_commits = list()


def cache_commits():
    global _commits
    if _commits:
        return _commits
    repo = Repo(structured_submissions)
    _commits = list(reversed(list(repo.iter_commits())))
    return _commits


def get_class_at_state(submission_name: str, class_name: str, state: CommitState) -> Tuple[str, error]:
    commits = cache_commits()
    if len(commits) < state + 1:
        return "", "Commit not found"
    idx = state
    if state == CommitState.FIXES:
        idx = -1
    commit = commits[idx]
    for tree in commit.tree.trees:
        if tree.name == submission_name:
            for blob in tree.blobs:
                if blob.name == f"{class_name}.java":
                    return blob.data_stream.read().decode("utf8"), ""
            return "", "File not found"
    return "", "Submission not found"
