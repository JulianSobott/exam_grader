import logging
import os
import re
import sys
from pathlib import Path
from typing import NewType


def _get_env_folder(env_name: str, not_exists_ok=True):
    if not os.environ.get(env_name):
        if not_exists_ok:
            return None
        else:
            raise FileNotFoundError(f"{env_name} variable is not set")

    path = Path(os.environ[env_name])
    if not path.exists() and not not_exists_ok:
        raise FileNotFoundError(f"{path} does not exist")
    if not path.is_dir() and not not_exists_ok:
        raise FileNotFoundError(f"{path} is not a directory")
    return path


submission_folder = _get_env_folder("submission_folder")
submission_raw_folder = _get_env_folder("submission_raw_folder", not_exists_ok=True)
project_folder = Path(__file__).parent.parent.parent
build_folder = project_folder.joinpath("build")
test_report_folder = build_folder.joinpath("reports")
gradings_file = test_report_folder.joinpath("gradings.json")
empty_java_classes_folder = project_folder.joinpath("src/empty")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
log_format = logging.Formatter('%(message)s')
handler.setFormatter(log_format)
logger.addHandler(handler)

error = NewType("error", str)


def iter_submissions_folders():
    for folder in submission_folder.iterdir():
        if folder.is_dir() and re.findall(r"(\w+)-([0-9]{4})", folder.name):
            yield folder


def submission_names(in_sub_list: list):
    out_sub_list = []
    for folder in iter_submissions_folders():
        name = folder.name
        contains = len([word for word in in_sub_list if word.lower() in name.lower()]) > 0
        if contains:
            out_sub_list.append(name)
    return out_sub_list
