import re

from config.local_config import get_local_config

_config = get_local_config()
raw_submissions = _config.submissions_folder.joinpath("raw")
structured_submissions = _config.submissions_folder.joinpath("structured")
submission_results_folder = _config.submissions_folder.joinpath("results")
empty_java_classes = _config.reference_project.joinpath("src/empty")


def iter_submissions_folders():
    for folder in structured_submissions.iterdir():
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
