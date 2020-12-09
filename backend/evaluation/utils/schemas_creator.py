import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set, Tuple

from utils.web_requests_schema_parser import schema_to_json_schemas


@dataclass
class AttributeObj:
    name: str
    type: str
    required: bool


@dataclass
class ClassObject:
    name: str
    attributes: List[AttributeObj]


@dataclass
class Dependency:
    dependencies: List['Dependency'] = field(default_factory=list)
    class_object: ClassObject = None


helper_class_counter = 0
helper_class_name = "_HelperClass"


def schema_to_python_dataclasses(schema: str) -> str:
    json_schemas = schema_to_json_schemas(schema)
    python_classes = []
    all_classes = set()

    def process_json_schema(s: dict):
        classes, all_c = json_schema_to_python_dataclasses(s)
        python_classes.append(classes)
        all_classes.update(all_c)

    for json_schema in json_schemas:
        process_json_schema(json_schema["request"])
        process_json_schema(json_schema["response"])
    header = f"# Auto generated code by script: schemas_creator.py\n"
    imports = "from dataclasses_json import dataclass_json\n" \
              "from dataclasses import dataclass\n" \
              "from typing import List, Union, Optional\n\n\n"
    all_str = "__all__ = [" + ", ".join(all_classes) + "]\n\n\n"
    file_content = header + imports + all_str + "".join(python_classes)
    return file_content


def json_schema_to_python_dataclasses(schema: dict) -> Tuple[str, set]:
    tree = Dependency()
    parse_object(schema, tree)
    all_classes = set()
    classes = generate_classes(tree.dependencies[0], all_classes)
    return classes, all_classes


def parse_property(p: dict, tree: Dependency) -> str:
    if p["type"] == "object":
        sub_class = parse_object(p, tree)
        p_type = sub_class.name
    elif p["type"] == "array":
        p_p_type = parse_property(p["items"], tree)
        p_type = f"List[{p_p_type}]"
    else:  # standard
        p_type = {"string": "str", "integer": "int", "number": "Union[int, float]", "boolean": "bool"}[p["type"]]
    return p_type


def parse_object(obj: dict, tree: Dependency) -> ClassObject:
    global helper_class_counter
    assert obj["type"] == "object"
    this_dep = Dependency()
    if obj.get("title"):
        class_name = to_camel_case(obj.get("title"))
    else:
        class_name = f"{helper_class_name}{helper_class_counter}"
        helper_class_counter += 1

    attributes = []
    for p_name, p in obj["properties"].items():
        p_type = parse_property(p, this_dep)
        required = p_name in obj.get("required", [])
        attribute = AttributeObj(p_name, p_type, required)
        attributes.append(attribute)
    class_obj = ClassObject(class_name, attributes)
    this_dep.class_object = class_obj
    tree.dependencies.append(this_dep)
    return class_obj


def generate_classes(root: Dependency, all_classes: Set[str]) -> str:
    classes = ""
    for child in root.dependencies:
        classes += generate_classes(child, all_classes)
    c = root.class_object
    if helper_class_name not in c.name:
        all_classes.add(f'"{c.name}"')
    class_str = f"@dataclass_json\n@dataclass\nclass {c.name}:\n"
    required = []
    optional = []
    for a in c.attributes:
        if a.required:
            attribute_str = f"{a.name}: {a.type}"
            required.append(attribute_str)
        else:
            default_value = {"str": '""', "int": "0", "bool": "False"}.get(a.type, "None")
            attribute_str = f"{a.name}: Optional[{a.type}] = {default_value}"
            optional.append(attribute_str)
    for attribute_str in required + optional:  # optional after required
        class_str += f"    {attribute_str}\n"
    if not required and not optional:
        class_str += f"    pass\n"
    class_str += "\n\n"
    classes += class_str
    return classes


def convert_all(src_folder: Path, dest_folder_json: Path, dest_folder_python: Path):
    for file in src_folder.iterdir():
        with open(file, "r") as f:
            text = f.read()
            json_schemas = schema_to_json_schemas(text)
            for schema in json_schemas:
                write_json_schema_file(f"{schema['name']}_request", dest_folder_json, schema["request"])
                write_json_schema_file(f"{schema['name']}_response", dest_folder_json, schema["response"])
            python_content = schema_to_python_dataclasses(text)
            name = file.name.replace('.schema', '')
            write_python_schema_file(name, dest_folder_python, python_content)


def write_json_schema_file(name: str, dest_folder: Path, schema: dict):
    text = json.dumps(schema, indent=2)
    write_file(f"{name}.schema.json", dest_folder, text)


def write_python_schema_file(name: str, dest_folder: Path, text: str):
    write_file(f"{name}_schema.py", dest_folder, text)


def write_file(name: str, dest_folder: Path, text: str):
    with open(dest_folder.joinpath(f"{name}"), "w") as f:
        f.write(text)


def to_camel_case(text: str) -> str:
    return "".join(map(str.title, text.split("_")))


if __name__ == '__main__':
    root_folder = Path(__file__).parents[3]
    python_src = root_folder.joinpath("backend").joinpath("evaluation")
    convert_all(
        root_folder.joinpath("schemas").joinpath("api_schemas"),
        root_folder.joinpath("schemas").joinpath("gen_json"),
        python_src.joinpath("schema_classes")
    )
