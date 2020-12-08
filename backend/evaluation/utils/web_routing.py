from dataclasses import dataclass
from typing import Callable, List
from flask import Flask


@dataclass
class SimpleRoute:
    rule: str
    function: Callable
    options: dict


def routes(app: Flask, *all_routes: List[SimpleRoute]):
    for r1 in all_routes:
        for r2 in r1:
            app.add_url_rule(r2.rule, r2.function.__name__, r2.function, **r2.options)


def group(rule: str, *sub_routes: List[SimpleRoute]) -> List[SimpleRoute]:
    new_routes = []
    for r_list in sub_routes:
        for r in r_list:
            r.rule = rule + r.rule
            new_routes.append(r)
    return new_routes


def route(rule: str, function, **options) -> List[SimpleRoute]:
    return [SimpleRoute(rule, function, options)]


def get(rule: str, function, **options) -> List[SimpleRoute]:
    return route(rule, function, methods=["GET"], **options)


def post(rule: str, function, **options) -> List[SimpleRoute]:
    return route(rule, function, methods=["POST"], **options)

