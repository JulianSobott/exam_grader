from enum import Enum
from typing import List


class AccessModifier(Enum):
    PRIVATE = "private"
    PROTECTED = "protected"
    PUBLIC = "public"
    DEFAULT = ""


def access_modifier_matched(actual: str, allowed: List[AccessModifier]) -> bool:
    for a in allowed:
        if actual == a.value:
            return True
    if actual is None and AccessModifier.DEFAULT in allowed:
        return True
    return False


def abstract_matched(actual: str, is_abstract: bool):
    return any_bool_match(actual, is_abstract)


def static_match(actual: str, is_static: bool) -> bool:
    return any_bool_match(actual, is_static)


def match_lists(a: list, b: list, ordered: bool) -> bool:
    if len(a) != len(b):
        return False
    if not ordered:
        a.sort()
        b.sort()
    for ea, eb in zip(a, b):
        if ea != eb:
            return False
    return True


def any_bool_match(actual: str, needed: bool) -> bool:
    if (needed and not actual) or (not needed and actual):
        return False
    return True
