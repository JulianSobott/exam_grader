from dataclasses import field
from typing import Tuple

from utils.web_requests_schema_parser.intermediate_representation import *
from utils.web_requests_schema_parser.parser import parse
from utils.web_requests_schema_parser.templates import Template


@dataclass
class PyAttribute(Template):
    name: str
    type: str
    init_code: str = None
    _template = "$name: $type $init_code"

    def init_code_to_str(self):
        return f"= {self.init_code}" if self.init_code else ""


@dataclass
class PyClass(Template):
    name: str
    attributes: List[PyAttribute]
    _template = """
@dataclass_json
@dataclass
class $name:
    $attributes
"""

    def attributes_to_str(self):
        if not self.attributes:
            return "pass"
        else:
            return self.sub(self.attributes)


@dataclass
class PyEnum(Template):
    name: str
    values: List[str]
    _template = """
class $name(Enum):
    $values
"""

    def values_to_str(self):
        return "\n".join([f"{v} = \"{v}\"" for v in self.values])


@dataclass
class PyFile(Template):
    classes: List[PyClass]
    enums: List[PyEnum]
    _template = """
# Auto generated code by script
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from enum import Enum
from typing import List, Union, Optional

__all__ = $all

$enums
$classes
"""

    def all_to_str(self):
        names = ['"' + c.name + '"' for c in self.classes + self.enums]
        return "[" + ", ".join(names) + "]"


type_mapping = {
    StringType: "str",
    IntType: "int",
    FloatType: "float",
    BooleanType: "bool"
}


@dataclass
class Tree:
    element: Template = None
    children: List["Tree"] = field(default_factory=list)

    def extract_enums_and_classes(self, enums: List[PyEnum], classes: List[PyClass]):
        for child in self.children:
            child.extract_enums_and_classes(enums, classes)
        if self.element is None:
            return
        if isinstance(self.element, PyClass):
            classes.append(self.element)
        elif isinstance(self.element, PyEnum):
            enums.append(self.element)
        else:
            raise TypeError(self.element)


def schema_to_python(text: str) -> str:
    file = parse(text)
    root = Tree()
    for global_type in file.global_types:
        child = type_definition_to_python(global_type)
        root.children.append(child)
    for communication in file.communications:
        children = communication_to_python(communication)
        root.children.extend(children)
    classes = []
    enums = []
    root.extract_enums_and_classes(enums, classes)
    py_file = PyFile(classes, enums)
    return py_file.to_str()


def communication_to_python(communication: Communication) -> List[Tree]:
    name = communication.name
    trees = []
    for req in communication.request.requests:
        if req.body:
            attributes, children = body_to_python(req.body)
            class_name = f"{to_camel_case(name)}{req.method}Request"
            py_class = PyClass(class_name, attributes)
            trees.append(Tree(py_class, children))
    resp_class_names = []
    for resp in communication.response.responses:
        if resp.body:
            attributes, children = body_to_python(resp.body)
            class_name = f"{to_camel_case(name)}{resp.code}Response"
            resp_class_names.append(class_name)
            py_class = PyClass(class_name, attributes)
            trees.append(Tree(py_class, children))
    class_name = f"{to_camel_case(name)}Response"
    attr_type = f"Union[" + ", ".join(['"' + name + '"' for name in resp_class_names]) + "]"
    trees.append(Tree(PyClass(class_name, [PyAttribute("data", attr_type)])))
    return trees


def type_definition_to_python(type_definition: TypeDefinition) -> Tree:
    name = type_definition.name
    if type_definition.type_type == ObjectType:
        attributes, children = body_to_python(type_definition.data.body)
        return Tree(PyClass(name, attributes), children)
    elif type_definition.type_type == EnumType:
        return Tree(PyEnum(type_definition.name, type_definition.data.values))
    else:
        raise NotImplemented("type definitions other than enum and object are not implemented yet")


def body_to_python(body: Body) -> Tuple[List[PyAttribute], List[Tree]]:
    attributes = []
    children = []
    for attr in body.attributes:
        t = attr.type_definition.type_type
        if t == ObjectType or t == EnumType:
            child = type_definition_to_python(attr.type_definition)
            children.append(child)
            assert isinstance(child.element, PyClass) or isinstance(child.element, PyEnum)
            py_type = child.element.name
        elif t == ReferenceType:
            py_type = attr.type_definition.data.name  # TODO
        else:
            assert t in type_mapping, f"{t} not in type_mapping"
            py_type = type_mapping[t]
        init_code = "None" if attr.is_optional else None
        if attr.is_array:
            py_type = f"List[{py_type}]"
        attributes.append(
            PyAttribute(attr.name, py_type, init_code)
        )
    return attributes, children


def to_camel_case(text: str) -> str:
    if "_" not in text:
        return text[0].upper() + text[1:]
    return "".join(map(str.title, text.split("_")))
