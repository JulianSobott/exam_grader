import re
from pathlib import Path
import chardet
import os
import shutil

from common import iter_submissions_folders, empty_java_classes_folder, submission_raw_folder
from test_code_mapping import required_files
from gittools import submission_folder, git_copied_files
from utils.project_logging import get_logger
from utils.p_types import error, new_error


def task_copy_files(raw_folder: Path, destination_folder: Path):
    copy_files(raw_folder, destination_folder)
    test_files()
    git_copied_files()


def copy_files(raw_folder: Path, destination_folder: Path, fail_fast: bool = True) -> error:
    logger = get_logger("preparation")
    if not raw_folder.exists():
        return new_error(f"Raw folder does not exist: {raw_folder}", logger)
    logger.info("Copying files...")
    for file in raw_folder.iterdir():
        match = re.match(r"(?P<students_name>\w+)(?P<mat_nr>[0-9]{4})_question_\d+_\d+_(?P<file_name>.*)", file.name)
        if not match:
            if fail_fast:
                return new_error(f"Invalid file name: {file.name}", logger)
            logger.warn(f"Invalid file name: {file.name}")
            continue
        submission_name = f"{match.group('students_name')}-{match.group('mat_nr')}"
        file_name = match.group('file_name')
        sub_folder = destination_folder.joinpath(submission_name)
        sub_folder.mkdir(parents=True, exist_ok=True)
        src = file
        dst = sub_folder.joinpath(file_name)
        if not dst.exists():
            _copy_file_utf8(src, dst)
        else:
            logger.debug(f"File already exists and is skipped: {dst}")


def _copy_file_utf8(src: Path, dst: Path, ):
    """
    copy the files. But ensure they are utf-8 encoded
    """
    with open(src, "rb") as f_src:
        with open(dst, "wb") as f_dst:
            content = f_src.read()
            encoding = chardet.detect(content)["encoding"]
            f_dst.write(content.decode(encoding).encode("utf-8"))


def test_files():
    logger.info("[test_files] Testing...")
    missing_files, wrong_named = get_file_failures()
    fails = [("w", f) for f in wrong_named] + [("m", f) for f in missing_files]
    prev_folder = ""
    for f in sorted(fails, key=lambda f: f[1]["folder"]):
        if f[1]["folder"] != prev_folder:
            print("")
        prev_folder = f[1]["folder"]
        path = f"{f[1]['folder'].name}/{f[1]['file']}"
        if f[0] == "w":
            logger.info(f"[test_files] Wrong named file: {path}")
        else:
            logger.info(f"[test_files] Missing file: {path}")


def get_file_failures():
    missing_files = []
    wrong_named = []
    for sub_folder in iter_submissions_folders():
        actual_files = os.listdir(sub_folder.absolute())
        for f in required_files:
            if f not in actual_files:
                missing_files.append({"file": f, "folder": sub_folder})
        for f in actual_files:
            if f not in required_files:
                wrong_named.append({"file": f, "folder": sub_folder})
    return missing_files, wrong_named


def fill_missing_files():
    logger.info("[fill_missing_files] Filling...")
    for missing in get_file_failures()[0]:
        logger.info(f"[fill_missing_files] Missing file: {missing['folder']}/{missing['file']} ."
                    f" An minimal compileable class will be added")
        shutil.copy2(empty_java_classes_folder.joinpath(missing['file']), missing['folder'])
    git_filled_files()


def renamed_files():
    git_renamed_files()
    fill_missing_files()
