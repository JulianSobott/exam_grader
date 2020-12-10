# from gittools import git_copied_files, git_filled_files, git_fixed_code, git_renamed_files
# from testing import run_tests_for_all, run_tests_for_submissions
from preparation import fill_missing_files, get_file_failures, cli_output_file_failures, rename_files, \
    copy_raw_to_structured

# from grading_reports import create_exel_table

__all__ = [
    "get_file_failures", "fill_missing_files", "cli_output_file_failures", "rename_files", "copy_raw_to_structured",
    # "git_fixed_code", "git_copied_files", "git_renamed_files", "git_filled_files",
    # "run_tests_for_all", "run_tests_for_submissions",
    "start_webserver",
    # "create_exel_table"
]


def start_webserver():
    from webserver import app
    app.run()

