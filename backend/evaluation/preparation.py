import os
import re
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

import chardet

from common import iter_submissions_folders, empty_java_classes, structured_submissions, raw_submissions
from config.exam_config import get_required_files
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
    return copy_raw_to_structured(raw_submissions, structured_submissions)


def _copy_file_utf8(src: Path, dst: Path, ):
    """
    copy the files. But ensure they are utf-8 encoded
    """
    with open(src, "rb") as f_src:
        with open(dst, "wb") as f_dst:
            content = f_src.read()
            encoding = chardet.detect(content)["encoding"]
            f_dst.write(content.decode(encoding).encode("utf-8"))


def cli_output_file_failures():
    logger.info("Testing filenames...")
    fails, err = get_file_failures()
    if err:
        logger.error(err)
        return
    prev_submission_name = ""
    for f in sorted(fails, key=lambda file: f.submission_name):
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
