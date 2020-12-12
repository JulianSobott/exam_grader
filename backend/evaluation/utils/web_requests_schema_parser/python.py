from dataclasses import field
from typing import Tuple

from utils.web_requests_schema_parser.intermediate_representation import *
from utils.web_requests_schema_parser.parser import parse
from utils.web_requests_schema_parser.templates import Template


class Request:

    def get(self, data: 'RequestGet') -> 'Response':
        ...


@dataclass
class PyRequestMethod(Template):
    name: str
    data_type: str
    return_type: str
    _template = """
@abstractmethod
def $name(self, data: $data_type) -> "$return_type":
    ...
"""


@dataclass
class PyRequestClass(Template):
    name: str
    methods: List[PyRequestMethod]
    _template = """
class $name(ABC):
    $methods
"""


@dataclass
class PyAttribute(Template):
    name: str
    type: str
    init_code: str = None
    _template = "$name: $type $init_code"

    def init_code_to_str(self):
        return f"= {self.init_code}" if self.init_code else ""


@dataclass
class PyVariable(Template):
    name: str
    value: str
    _template = "$name = $value"


@dataclass
class PyDataClass(Template):
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
    classes: List[PyDataClass]
    enums: List[PyEnum]
    variables: List[PyVariable]
    _template = """
# Auto generated code by script
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from enum import Enum
from typing import List, Union, Optional
from abc import ABC, abstractmethod


__all__ = $all

$enums
$classes
$variables
"""

    def all_to_str(self):
        names = ['"' + c.name + '"' for c in self.classes + self.enums + self.variables]
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

    def extract_enums_and_classes(self, enums: List[PyEnum], classes: List[PyDataClass], variables: List[PyVariable]):
        for child in self.children:
            child.extract_enums_and_classes(enums, classes, variables)
        if self.element is None:
            return
        if isinstance(self.element, PyDataClass) or isinstance(self.element, PyRequestClass):
            classes.append(self.element)
        elif isinstance(self.element, PyEnum):
            enums.append(self.element)
        elif isinstance(self.element, PyVariable):
            variables.append(self.element)
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
    variables = []
    root.extract_enums_and_classes(enums, classes, variables)
    py_file = PyFile(classes, enums, variables)
    return py_file.to_str()


def communication_to_python(communication: Communication) -> List[Tree]:
    name = to_camel_case(communication.name)
    trees = []
    methods = []
    for req in communication.requests:
        gen_class_name = f"{name}{req.method}"
        attributes, children = body_to_python(req.parameters)
        req_class_name = f"{gen_class_name}Request"
        py_class = PyDataClass(req_class_name, attributes)
        trees.append(Tree(py_class, children))

        resp_class_names = []
        for resp in req.responses:
            attributes, children = body_to_python(resp.body)
            class_name = f"{gen_class_name}{resp.code}Response"
            resp_class_names.append(class_name)
            py_class = PyDataClass(class_name, attributes)
            trees.append(Tree(py_class, children))

        response_type_name = f"{gen_class_name}Response"
        response_type_value = f"Union[" + ", ".join(resp_class_names) + "]"
        trees.append(Tree(PyVariable(response_type_name, response_type_value)))
        method = PyRequestMethod(req.method.lower(), req_class_name, response_type_name)
        methods.append(method)
    trees.append(Tree(PyRequestClass(f"{name}Request", methods)))
    return trees


def type_definition_to_python(type_definition: TypeDefinition) -> Tree:
    name = type_definition.name
    if type_definition.type_type == ObjectType:
        attributes, children = body_to_python(type_definition.data.body)
        return Tree(PyDataClass(name, attributes), children)
    elif type_definition.type_type == EnumType:
        return Tree(PyEnum(type_definition.name, type_definition.data.values))
    else:
        raise NotImplemented("type definitions other than enum and object are not implemented yet")


def body_to_python(body: Body) -> Tuple[List[PyAttribute], List[Tree]]:
    attributes = []
    children = []
    if body is None:
        return attributes, children
    for attr in body.attributes:
        t = attr.type_definition.type_type
        if t == ObjectType or t == EnumType:
            child = type_definition_to_python(attr.type_definition)
            children.append(child)
            assert isinstance(child.element, PyDataClass) or isinstance(child.element, PyEnum)
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
