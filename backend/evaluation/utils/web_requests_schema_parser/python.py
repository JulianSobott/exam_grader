from dataclasses import field
from typing import Tuple

import autopep8

from utils.web_requests_schema_parser.intermediate_representation import *
from utils.web_requests_schema_parser.parser import parse
from utils.web_requests_schema_parser.templates import Template


@dataclass
class PyHandleMethod(Template):
    name: str
    data_type: str
    return_type: str
    _template = """
@abstractmethod
def handle_$name(self, data: "$data_type") -> "$return_type":
    ...
"""


@dataclass
class PyRequestMethod(Template):
    http_method: str
    data_type: str
    attributes: List["PyAttribute"]
    response_type: str
    code_class_map: dict
    _template = """
@classmethod
def $http_method(cls, $attributes) -> Tuple["$response_type", str]:
    data = $data_type($attribute_names)
    res = cls._request("$http_method", data)
    code_class_map = $code_class_map
    if res.status_code not in code_class_map:
        return res, "Unknown status returned"
    code_class = code_class_map[res.status_code]
    return code_class.from_json(res.text), ""
"""

    def code_class_map_to_str(self):
        return "{" + ", ".join(f"{code}: {class_}" for code, class_ in self.code_class_map.items()) + "}"

    def attributes_to_str(self):
        return ", ".join([a.to_str() for a in get_ordered_attributes(self.attributes)])

    def attribute_names_to_str(self):
        return ", ".join([a.name for a in get_ordered_attributes(self.attributes)])


@dataclass
class PyRequestClass(Template):
    name: str
    handle_methods: List[PyHandleMethod]
    request_methods: List[PyRequestMethod]
    uri: str
    _template = """
class $name(ABC):
    _json_mapper = $json_mapper
    _url = "http://127.0.0.1:5000/api/v1$uri"
    
    def __init__(self, request):
        self.request = request
    
    @classmethod
    def _handle_request(cls, request):
        method = request.method.lower()
        instance = cls(request)
        data_class = instance._json_mapper[method]
        json_data = request.data
        data = None
        valid_json = False
        try:
            data = data_class.from_json(json_data)
            valid_json = True
        except:
            pass
        response_data = instance.__getattribute__(f"handle_{method}")(data)
        response = make_response(response_data.to_json(), response_data.status_code)
        response.mimetype = "application/json"
        return response
    
    @classmethod
    def _request(cls, method, data):
        return requests.request(method, cls._url, data=data.to_json())
        
    $handle_methods
    $request_methods
"""

    def json_mapper_to_str(self):
        return "{" + ", ".join([f"\"{m.name}\": {m.data_type}" for m in self.handle_methods]) + "}"


@dataclass
class PyAttribute(Template):
    name: str
    type: str
    init_code: str = None
    _template = "$name: \"$type\" $init_code"

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
            return self.sub(get_ordered_attributes(self.attributes))


def get_ordered_attributes(attributes: List[PyAttribute]):
    required = [a for a in attributes if not a.init_code]
    optional = [a for a in attributes if a.init_code]
    return required + optional


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
    objects: "Tree"
    _template = """
# Auto generated code by script
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from enum import Enum
from typing import List, Union, Optional, Tuple
from abc import ABC, abstractmethod
from flask import make_response
import requests


__all__ = $all


$objects
"""

    def all_to_str(self):
        elements = []
        queue = [self.objects]
        while queue:
            tree = queue.pop()
            queue.extend(tree.children)
            if tree.element:
                elements.append(tree.element)
        names = ['"' + c.name + '"' for c in elements]
        return "[" + ", ".join(names) + "]"


type_mapping = {
    StringType: "str",
    IntType: "int",
    FloatType: "float",
    BooleanType: "bool"
}


@dataclass
class Tree(Template):
    element: Template = None
    children: List["Tree"] = field(default_factory=list)
    _template = """
$children


$element    
"""

    def children_to_str(self):
        return "\n".join([s.to_str().strip() for s in self.children])


def schema_to_python(text: str) -> str:
    file = parse(text)
    root = Tree()
    for global_type in file.global_types:
        child = type_definition_to_python(global_type)
        root.children.append(child)
    for communication in file.communications:
        children = communication_to_python(communication)
        root.children.extend(children)
    py_file = PyFile(root)
    py_code = py_file.to_str()
    return autopep8.fix_code(py_code, options={"max_line_length": 120, "aggressive": 1})


def communication_to_python(communication: Communication) -> List[Tree]:
    name = to_camel_case(communication.name)
    endpoint_name = f"{name}RequestBase"
    trees = []
    handle_methods = []
    request_methods = []
    for req in communication.requests:
        gen_class_name = f"{name}{req.method}"
        req_attributes, children = body_to_python(req.parameters)
        req_class_name = f"{gen_class_name}Request"
        py_class = PyDataClass(req_class_name, req_attributes)
        trees.append(Tree(py_class, children))

        resp_class_names = []
        resp_code_class_map = {}
        for resp in req.responses:
            attributes, children = body_to_python(resp.body)
            class_name = f"{gen_class_name}{resp.code}Response"
            resp_class_names.append(class_name)
            attributes.append(PyAttribute("status_code", "int", resp.code))
            py_class = PyDataClass(class_name, attributes)
            trees.append(Tree(py_class, children))
            resp_code_class_map[resp.code] = class_name

        response_type_name = f"{gen_class_name}Response"
        response_type_value = f"Union[" + ", ".join(resp_class_names) + "]"
        trees.append(Tree(PyVariable(response_type_name, response_type_value)))
        method = PyHandleMethod(req.method.lower(), req_class_name, response_type_name)
        handle_methods.append(method)
        request_method = PyRequestMethod(req.method.lower(), req_class_name, req_attributes, response_type_name,
                                         resp_code_class_map)
        request_methods.append(request_method)
    uri = get_simple_attribute(communication.attributes, "uri", communication.name)
    request_class = PyRequestClass(endpoint_name, handle_methods, request_methods, uri)
    trees.append(Tree(request_class))
    return trees


def get_simple_attribute(attributes: List[SimpleAttribute], name: str, default=None):
    for a in attributes:
        if a.key == name:
            return a.value
    return default


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
