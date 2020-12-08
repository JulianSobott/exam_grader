from gittools import git_copied_files, git_filled_files, git_fixed_code, git_renamed_files
from testing import run_tests_for_all, run_tests_for_submissions
from preparation import copy_files, fill_missing_files, test_files, renamed_files
from grading_reports import create_exel_table

__all__ = [
    "copy_files", "fill_missing_files", "test_files", "renamed_files",
    "git_fixed_code", "git_copied_files", "git_renamed_files", "git_filled_files",
    "run_tests_for_all", "run_tests_for_submissions",
    "start_webserver",
    "create_exel_table"
]


def start_webserver():
    from webserver import app
    app.run()

