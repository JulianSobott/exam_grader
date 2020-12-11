from dataclasses import dataclass
from typing import List, Union


@dataclass
class ObjectType:
    body: 'Body'


@dataclass
class IntType:
    minimum: int = None
    maximum: int = None


@dataclass
class FloatType:
    minimum: float = None
    maximum: float = None


@dataclass
class StringType:
    pass


@dataclass
class BooleanType:
    pass


@dataclass
class EnumType:
    values: List[str]


@dataclass
class ReferenceType:
    name: str


@dataclass
class TypeDefinition:
    type_type: type
    data: Union[ObjectType, IntType, FloatType, StringType, BooleanType, EnumType]
    name: str = None


@dataclass
class Attribute:
    name: str
    type_definition: TypeDefinition
    is_optional: bool = False
    is_array: bool = False


@dataclass
class Body:
    attributes: List[Attribute]


@dataclass
class RequestMethod:
    method: str  # TODO: enum http methods
    body: Body


@dataclass
class Request:
    requests: List[RequestMethod]


@dataclass
class ResponseBody:
    code: int
    body: Body


@dataclass
class Response:
    responses: List[ResponseBody]


@dataclass
class Communication:
    name: str
    attributes: List["SimpleAttribute"]
    request: Request
    response: Response


@dataclass
class Constant:
    name: str
    value: str  # For now only string constants


@dataclass
class File:
    communications: List[Communication]
    global_types: List[TypeDefinition]
    constants: List[Constant]


@dataclass
class SimpleAttribute:
    key: str
    value: str
