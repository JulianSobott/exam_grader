from pathlib import Path
from typing import List

from utils.web_requests_schema_parser.python import schema_to_python
from utils.web_requests_schema_parser.to_js import schema_to_js


def convert_all(src_folder: Path, dest_folder_js: List[Path], dest_folder_python: List[Path]):
    for dest in dest_folder_python + dest_folder_js:
        dest.mkdir(parents=True, exist_ok=True)
    for file in src_folder.iterdir():
        with open(file, "r") as f:
            text = f.read()
            name = file.name.replace('.schema', '')

            python_content = schema_to_python(text)
            for dest in dest_folder_python:
                write_python_schema_file(name, dest, python_content)

            js_content = schema_to_js(text)
            for dest in dest_folder_js:
                write_js_schema_file(name, dest, js_content)


def write_js_schema_file(name: str, dest_folder: Path, text: str):
    write_file(f"{name}_schema.js", dest_folder, text)


def write_python_schema_file(name: str, dest_folder: Path, text: str):
    write_file(f"{name}_schema.py", dest_folder, text)


def write_file(name: str, dest_folder: Path, text: str):
    with open(dest_folder.joinpath(f"{name}"), "w") as f:
        f.write(text)


if __name__ == '__main__':
    root_folder = Path(__file__).parents[3]
    backend_src = root_folder.joinpath("backend").joinpath("evaluation")
    frontend_src = root_folder.joinpath("frontend")
    convert_all(
        root_folder.joinpath("schemas").joinpath("api_schemas"),
        [frontend_src.joinpath("static").joinpath("js").joinpath("schema_classes")],
        [backend_src.joinpath("schema_classes"), frontend_src.joinpath("schema_classes")]
    )
