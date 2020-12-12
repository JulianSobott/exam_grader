import json
from pathlib import Path
from typing import List

from utils.web_requests_schema_parser.python import schema_to_python


def convert_all(src_folder: Path, dest_folder_json: Path, dest_folder_python: List[Path]):
    for dest in dest_folder_python:
        dest.mkdir(parents=True, exist_ok=True)
    for file in src_folder.iterdir():
        with open(file, "r") as f:
            text = f.read()
            python_content = schema_to_python(text)
            name = file.name.replace('.schema', '')
            for dest in dest_folder_python:
                write_python_schema_file(name, dest, python_content)


def write_json_schema_file(name: str, dest_folder: Path, schema: dict):
    text = json.dumps(schema, indent=2)
    write_file(f"{name}.schema.json", dest_folder, text)


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
        root_folder.joinpath("schemas").joinpath("gen_json"),
        [backend_src.joinpath("schema_classes"), frontend_src.joinpath("schema_classes")]
    )
