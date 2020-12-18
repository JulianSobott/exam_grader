import re
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List

from static_code_testing.lib import AccessModifier, access_modifier_matched, abstract_matched, match_lists


class MethodFailure(IntEnum):
    NAME = 0
    ACCESS_MODIFIER = 1
    RETURN_TYPE = 2
    ABSTRACT = 3
    PARAMETERS = 4


@dataclass
class MethodTest:
    name: str
    access_modifiers: List[AccessModifier]
    return_type: str
    parameters: List[str] = field(default_factory=list)
    parameters_ordered: bool = True
    is_abstract: bool = False
    is_constructor: bool = False


def test_method(method: MethodTest, code: str) -> List[MethodFailure]:
    regex = re.compile(r"((?P<access_modifier>\w+)\s)?\s*((?P<abstract>abstract)\s)?\s*((?P<return_type>\w+)\s)\s*"
                       + method.name
                       + r"\s*\((?P<parameters>[^)]*)\)")
    match = regex.search(code)
    if match is None:
        return [MethodFailure.NAME]
    failures = []
    if not access_modifier_matched(match.group("access_modifier"), method.access_modifiers):
        failures.append(MethodFailure.ACCESS_MODIFIER)
    if not abstract_matched(match.group("abstract"), method.is_abstract):
        failures.append(MethodFailure.ABSTRACT)
    if method.is_constructor and match.group("return_type"):
        failures.append(MethodFailure.RETURN_TYPE)
    if not method.is_constructor and method.return_type != match.group("return_type"):
        failures.append(MethodFailure.RETURN_TYPE)
    # parameters
    actual_parameter_types = []
    for p in match.group("parameters").split(","):
        actual_parameter_types.append(p.strip(" ").split(" ")[0])
    if not match_lists(actual_parameter_types, method.parameters, method.parameters_ordered):
        failures.append(MethodFailure.PARAMETERS)
    return failures
