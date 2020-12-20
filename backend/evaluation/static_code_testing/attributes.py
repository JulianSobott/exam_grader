import re
from dataclasses import dataclass
from enum import IntEnum
from typing import List

from static_code_testing.lib import AccessModifier, access_modifier_matched, static_match


class AttributeFailure(IntEnum):
    NAME = 0
    ACCESS_MODIFIER = 1
    TYPE = 2
    STATIC = 3


@dataclass
class AttributeTest:
    name: str
    type: str
    access_modifiers: List[AccessModifier]
    is_static: bool = False


def test_attribute(attribute: AttributeTest, code: str) -> List[AttributeFailure]:
    regex = re.compile(r"((?P<access_modifier>\w+)\s)?\s*((?P<static>static)\s)?\s*((?P<type>\w+(\[])?\s)\s*"
                       + attribute.name
                       + r"\s*(=\s*(?P<default_value>[^;]*))?;")
    match = regex.search(code)
    if match is None:
        return [AttributeFailure.NAME]
    failures = []
    if not access_modifier_matched(match.group("access_modifier"), attribute.access_modifiers):
        failures.append(AttributeFailure.ACCESS_MODIFIER)
    if match.group("type") != attribute.type:
        failures.append(AttributeFailure.TYPE)
    if not static_match(match.group("static"), attribute.is_static):
        failures.append(AttributeFailure.STATIC)
    return failures
