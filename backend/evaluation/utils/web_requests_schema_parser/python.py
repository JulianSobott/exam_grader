from dataclasses import dataclass
from typing import List

from utils.web_requests_schema_parser.parser import parse
from utils.web_requests_schema_parser.templates import Template


@dataclass
class PyAttribute(Template):
    name: str
    type: str
    init_code: str = None
    _template = "$name: $type $init_code"

    def initializor_code_to_str(self):
        return f"= {self.init_code}" if self.init_code else ""


@dataclass
class PyClass(Template):
    name: str
    attributes: List[PyAttribute]
    _template = """
@dataclass
@dataclass_json
class $name:
    $attributes
"""


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


def schema_to_python(text: str) -> str:
    code = ""
    file = parse(text)


if __name__ == '__main__':
    s = PyClass("Test", [PyAttribute("attr1", "str"), PyAttribute("attr2", "str", "\"new\"")])
    s2 = PyClass("Test", [PyAttribute("attr1", "str"), PyAttribute("attr2", "str", "\"new\"")])
    e = PyEnum("my_name", ["NOT_NOW", "OK"])
    print(PyFile([s, s2], [e]).to_str())
