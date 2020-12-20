from dataclasses import dataclass
from random import random
from typing import Callable, List

from flask import Flask, request

from api import todo


@dataclass
class SimpleRoute:
    rule: str
    name: str
    function: Callable
    options: dict


def routes(app: Flask, *all_routes: List[SimpleRoute]):
    for r1 in all_routes:
        for r2 in r1:
            app.add_url_rule(r2.rule, r2.name, r2.function, **r2.options)


def group(rule: str, *sub_routes: List[SimpleRoute]) -> List[SimpleRoute]:
    new_routes = []
    for r_list in sub_routes:
        for r in r_list:
            r.rule = rule + r.rule
            new_routes.append(r)
    return new_routes


def _route(rule: str, request_class, method: str, **options) -> List[SimpleRoute]:
    def inner(*_, **url_params):
        return request_class._handle_request(request, url_params)

    function_name = f"{request_class}_{method}"
    if request_class == todo:
        function_name = function_name + str(random())
    return [SimpleRoute(rule, function_name, inner, options)]


def get(rule: str, function, **options) -> List[SimpleRoute]:
    return _route(rule, function, "get", methods=["GET"], **options)


def post(rule: str, function, **options) -> List[SimpleRoute]:
    return _route(rule, function, "post", methods=["POST"], **options)
