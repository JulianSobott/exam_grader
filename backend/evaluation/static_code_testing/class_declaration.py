import re
from dataclasses import dataclass, field
from enum import IntEnum, Enum
from typing import List

from static_code_testing.lib import AccessModifier, access_modifier_matched, abstract_matched, match_lists


class ClassFailure(IntEnum):
    NAME = 0
    ACCESS_MODIFIER = 1
    TYPE = 2
    ABSTRACT = 3
    EXTENDS = 4
    IMPLEMENTS = 5


class ClassType(Enum):
    INTERFACE = "interface"
    CLASS = "class"


@dataclass
class ClassTest:
    name: str
    extends: str = None
    implements: List[str] = field(default_factory=list)
    is_abstract: bool = False
    access_modifiers: List[AccessModifier] = field(default_factory=lambda: [AccessModifier.PUBLIC])
    class_type: ClassType = ClassType.CLASS


def test_class(cls: ClassTest, code: str) -> List[ClassFailure]:
    regex = re.compile(r"((?P<access_modifier>\w+)\s)?\s*((?P<abstract>abstract)\s)?\s*((?P<type>\w+)\s)\s*"
                       + cls.name
                       + r"\s*(?P<inheritance>[^{]*)")
    match = regex.search(code)
    if match is None:
        return [ClassFailure.NAME]
    failures = []
    if not access_modifier_matched(match.group("access_modifier"), cls.access_modifiers):
        failures.append(ClassFailure.ACCESS_MODIFIER)
    if not abstract_matched(match.group("abstract"), cls.is_abstract):
        failures.append(ClassFailure.ABSTRACT)
    if match.group("type") != cls.class_type.value:
        failures.append(ClassFailure.TYPE)

    # inheritance
    inheritance = match.group("inheritance") if match.group("inheritance") else ""
    inheritance = re.sub(r"\s+", " ", inheritance)

    # implements
    interfaces = []
    if "implements" in inheritance:
        interfaces = inheritance.split("implements")[-1].split(",")
        interfaces = list(map(str.strip, interfaces))
    if not match_lists(interfaces, cls.implements, False):
        failures.append(ClassFailure.IMPLEMENTS)

    # extends
    parent = None
    if "extends" in inheritance:
        temp = inheritance.split(" ")
        parent = temp[temp.index("extends") + 1]
    if cls.extends != parent:
        failures.append(ClassFailure.EXTENDS)

    return failures
