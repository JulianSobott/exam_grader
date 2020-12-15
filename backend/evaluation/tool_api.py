from gittools import git_copied_files, git_filled_files, git_fixed_code, git_renamed_files
from grading.serialization import create_exel_table
from preparation import fill_missing_files, get_file_failures, cli_output_file_failures, rename_files, \
    copy_raw_to_structured, save_submissions
from testing import run_tests_for_all, run_tests_for_submissions

__all__ = [
    "get_file_failures", "fill_missing_files", "cli_output_file_failures", "rename_files", "copy_raw_to_structured",
    "save_submissions",
    "git_fixed_code", "git_copied_files", "git_renamed_files", "git_filled_files",
    "run_tests_for_all", "run_tests_for_submissions",
    "start_webserver",
    "create_exel_table"
]


def start_webserver():
    from webserver import app
    app.run()

