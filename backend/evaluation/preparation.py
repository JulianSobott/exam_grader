import os
import re
import shutil
import zipfile
from pathlib import Path
from typing import List, Optional, Tuple

from charset_normalizer import CharsetNormalizerMatches as CnM

from common import iter_submissions_folders, empty_java_classes, structured_submissions, raw_submissions
from config.exam_config import get_required_files, get_exam_config_else_raise, ExamConfig, \
    CodeSnippetConfig, CodeType
from data.api import insert_submission
from data.schemas import Submission, Student, Subtask, Task, CodeSnippet
from get_code import get_method_code, get_attributes_code, get_class_header_code, get_constructor_code, CodeStatus, \
    get_full_class
from gittools import git_copied_files, git_renamed_files, git_filled_files
from schema_classes.overview_schema import GradingStatus
from schema_classes.tools_schema import FileError, FileErrorType, RenameFile
from utils.p_types import error, new_error
from utils.project_logging import get_logger

logger = get_logger(__name__)


def copy_raw_to_structured(raw_folder: Path, structured_folder: Path) -> error:
    """
    No files are copied, when one or more files are not recognized as submission files. i.e. do not have a file name,
    that is matched by the regular expression.
    :param raw_folder:
    :param structured_folder:
    :return:
    """
    file_regex = re.compile(r"(?P<students_name>\w+)(?P<mat_nr>[0-9]{4})_question_\d+_\d+_(?P<file_name>.*)")
    raw_folder.mkdir(parents=True, exist_ok=True)
    for file in raw_folder.iterdir():
        match = file_regex.match(file.name)
        if not match:
            return new_error(f"Invalid file name: {file.name}", logger)
    logger.info("Copying files...")
    for file in raw_folder.iterdir():
        match = file_regex.match(file.name)
        submission_name = f"{match.group('students_name')}-{match.group('mat_nr')}"
        file_name = match.group('file_name')
        sub_folder = structured_folder.joinpath(submission_name)
        sub_folder.mkdir(parents=True, exist_ok=True)
        src = file
        dst = sub_folder.joinpath(file_name)
        if not dst.exists():
            _copy_file_utf8(src, dst)
        else:
            logger.debug(f"File already exists and is skipped: {dst}")


def task_copy_raw_to_structured() -> error:
    err = copy_raw_to_structured(raw_submissions, structured_submissions)
    if not err:
        git_copied_files()
    return err


def task_renamed_files():
    save_submissions()
    git_renamed_files()
    err = fill_missing_files()
    if not err:
        git_filled_files()


def _copy_file_utf8(src: Path, dst: Path, ):
    """
    copy the files. But ensure they are utf-8 encoded
    """
    renames = {"ü": "ue", "ä": "ae", "ö": "oe", "ß": "ss"}
    with open(src, "rb") as f_src:
        match = CnM.from_fp(f_src)
    with open(dst, "w", encoding="utf-8") as f_dst:
        content = str(match.best().first())
        for old, new in renames.items():
            content = content.replace(old, new)
            content = content.replace(old.title(), new.title())
        f_dst.write(content)


def cli_output_file_failures():
    logger.info("Testing filenames...")
    fails, err = get_file_failures()
    if err:
        logger.error(err)
        return
    prev_submission_name = ""
    for f in sorted(fails, key=lambda file: file.submission_name):
        if f.submission_name != prev_submission_name:
            print("")
        prev_submission_name = f.submission_name
        path = f"{f.submission_name}/{f.file_name}"
        mapping = {FileErrorType.WRONG_NAMED: "Wrong named", FileErrorType.MISSING: "Missing"}
        logger.info(f"{mapping[f.failure_type]} file: {path}")


def get_file_failures() -> Tuple[Optional[List[FileError]], error]:
    failures = []
    required_files, err = get_required_files()
    if err:
        return None, err
    for sub_folder in iter_submissions_folders():
        actual_files = os.listdir(sub_folder.absolute())
        for f in required_files:
            if f not in actual_files:
                failures.append(FileError(sub_folder.name, f, FileErrorType.MISSING))
        for f in actual_files:
            if f not in required_files:
                failures.append(FileError(sub_folder.name, f, FileErrorType.WRONG_NAMED))
    return failures, None


def fill_missing_files() -> error:
    failures, err = get_file_failures()
    if err:
        return err
    logger.info("Filling missing files...")
    for fail in failures:
        if fail.failure_type == FileErrorType.MISSING:
            src = empty_java_classes.joinpath(fail.file_name)
            if not src.exists():
                return new_error(f"src file does not exist: {src}", logger)
            logger.info(f"Missing file: {fail.submission_name}/{fail.file_name} ."
                        f" An minimal compileable class will be added")
            shutil.copy2(src,
                         structured_submissions.joinpath(fail.submission_name))


def rename_files(renames: List[RenameFile]) -> error:
    moves = []
    for rename in renames:
        sub_folder = structured_submissions.joinpath(rename.submission_name)
        old_file = sub_folder.joinpath(rename.original_name)
        if not old_file.exists():
            return new_error(f"file: {old_file} does not exist therefore can't be renamed", logger)
        moves.append((old_file, sub_folder.joinpath(rename.new_name)))
        # no files renamed, when one fails
    for move in moves:
        shutil.move(*move)
    return None


def save_submissions():
    """Saves all the data for a submission that is available after they are sorted into folders and before testing."""
    folder_regex = re.compile(r"(?P<students_name>\w+_\w+)-(?P<canvas_id>[0-9]{4})")
    exam = get_exam_config_else_raise()
    exam_name = exam.name

    for sub in structured_submissions.iterdir():
        match = folder_regex.match(sub.name)
        if match:
            tasks = get_tasks_with_code(sub.name, exam)
            students_name = match.group("students_name")
            canvas_id = match.group("canvas_id")
            default_bookmarked = False
            default_status_grading = GradingStatus.NOT_STARTED
            insert_submission(
                Submission(sub.name, exam_name, Student(students_name, canvas_id), tasks, default_bookmarked,
                           default_status_grading))
            logger.debug(f"Submission saved: {sub.name}")
        else:
            if sub.name not in [".git"]:
                logger.warning(f"Invalid file in {structured_submissions}: {sub.name}")


def get_tasks_with_code(submission_name: str, exam: ExamConfig) -> List[Task]:
    tasks = []
    for task_name, task_data in exam.tasks.items():
        subtasks = []
        task_max_points = 0
        for subtask_name, subtask_data in task_data.subtasks.items():
            code_snippets = code_snippets_for_subtask(submission_name, task_data.class_name, subtask_data.code_snippets)
            task_max_points += subtask_data.points
            default_points = 0
            default_bookmarked = False
            default_comment = ""
            subtasks.append(
                Subtask(subtask_name, subtask_data.description, subtask_data.points, default_points,
                        default_bookmarked, default_comment, code_snippets)
            )
        default_bookmarked = False
        description = None  # Use description from task_data, when added
        default_comment = ""
        full_code, status = get_full_class(structured_submissions.joinpath(submission_name), task_data.class_name)
        full_code = CodeSnippet(task_data.class_name, task_data.class_name, status == CodeStatus.ORIGINAL, full_code)
        tasks.append(
            Task(task_name, task_max_points, subtasks, default_bookmarked, default_comment, description, full_code)
        )
    return tasks


def code_snippets_for_subtask(submission_name: str, class_name: str, code_snippet_configs: List[CodeSnippetConfig]):
    code_folder = structured_submissions.joinpath(submission_name)
    code_snippets = []
    for snippet_config in code_snippet_configs:
        d = {
            CodeType.METHOD: {
                "function": lambda: get_method_code(code_folder, class_name, snippet_config.name),
                "name": snippet_config.name,
            },
            CodeType.ATTRIBUTES: {
                "function": lambda: get_attributes_code(code_folder, class_name),
                "name": "Attributes"
            },
            CodeType.CLASS_HEADER: {
                "function": lambda: get_class_header_code(code_folder, class_name),
                "name": "Class declaration"
            },
            CodeType.CONSTRUCTOR: {
                "function": lambda: get_constructor_code(code_folder, class_name),
                "name": "Constructor"
            },
            CodeType.CLASS: {
                "function": lambda: get_full_class(code_folder, class_name),
                "name": "Class"
            }
        }
        conf = d[snippet_config.code_type]
        code, code_status = conf["function"]()
        code_snippet = CodeSnippet(conf["name"], class_name, code_status == CodeStatus.ORIGINAL, code)
        code_snippets.append(code_snippet)
    return code_snippets


def task_extract_zip(path: Path) -> Tuple[Optional[List[FileError]], error]:
    with zipfile.ZipFile(path, "r") as f:
        f.extractall(raw_submissions)

    err = task_copy_raw_to_structured()
    if err:
        return None, err
    failures, err = get_file_failures()
    return failures, err


if __name__ == '__main__':
    task_copy_raw_to_structured()
