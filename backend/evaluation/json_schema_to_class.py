import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Set


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


def parse_schema(schema: dict) -> str:
    tree = Dependency()
    parse_object(schema, tree)
    all_classes = set()
    classes = generate_classes(tree.dependencies[0], all_classes)
    header = f"# Auto generated code by script: json_schema_to_class.py\n"
    imports = "from dataclasses_json import dataclass_json\n" \
              "from dataclasses import dataclass\n" \
              "from typing import List, Union, Optional\n\n\n"
    all_str = "__all__ = [" + ", ".join(all_classes) + "]\n\n\n"
    file_content = header + imports + all_str + classes
    return file_content


def parse_property(p: dict, tree: Dependency) -> str:
    if p["type"] == "object":
        sub_class = parse_object(p, tree)
        p_type = sub_class.name
    elif p["type"] == "array":
        p_p_type = parse_property(p["items"], tree)
        p_type = f"List[{p_p_type}]"
    else:   # standard
        p_type = {"string": "str", "integer": "int", "number": "Union[int, float]", "boolean": "bool"}[p["type"]]
    return p_type


def parse_object(obj: dict, tree: Dependency) -> ClassObject:
    assert obj["type"] == "object"
    this_dep = Dependency()
    class_name = obj.get("title", "RandomClassName")
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
    class_str += "\n\n"
    classes += class_str
    return classes


def generate(src_file_path: Path, dest_file_path: Path):
    with open(src_file_path, "r") as f:
        data = json.load(f)
        file_content = parse_schema(data)
    with open(dest_file_path, "w") as f:
        f.write(file_content)


if __name__ == '__main__':
    schemas = [
        (Path("schemas/gradings.schema.json"), Path("schema_classes/gradings_schema.py")),
        (Path("schemas/test_results.schema.json"), Path("schema_classes/test_results_schema.py")),
        (Path("schemas/web_data.schema.json"), Path("schema_classes/web_data_schema.py")),
    ]
    for schema in schemas:
        generate(schema[0], schema[1])
