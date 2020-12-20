from data.api import debug_reset_all_data
from gittools import git_copied_files, git_filled_files, git_fixed_code, git_renamed_files
from grading.serialization import create_exel_table
from preparation import fill_missing_files, get_file_failures, cli_output_file_failures, rename_files, \
    task_copy_raw_to_structured, save_submissions, task_renamed_files, task_extract_zip
from testing import run_tests_for_all, run_tests_for_submissions

__all__ = [
    "get_file_failures", "fill_missing_files", "cli_output_file_failures", "rename_files",
    "task_copy_raw_to_structured", "save_submissions", "task_renamed_files", "task_extract_zip",
    "git_fixed_code", "git_copied_files", "git_renamed_files", "git_filled_files",
    "run_tests_for_all", "run_tests_for_submissions",
    "start_webserver",
    "create_exel_table",
    "debug_reset_all"
]


def start_webserver():
    from webserver import app
    app.run()


def debug_reset_all():
    from common import structured_submissions, submission_results_folder
    import shutil
    debug_reset_all_data()
    shutil.rmtree(structured_submissions, ignore_errors=True)
    shutil.rmtree(submission_results_folder, ignore_errors=True)
