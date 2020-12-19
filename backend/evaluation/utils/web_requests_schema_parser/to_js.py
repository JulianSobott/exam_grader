from dataclasses import dataclass
from typing import List

from utils.web_requests_schema_parser.intermediate_representation import Communication, get_simple_attribute, \
    url_params_from_uri
from utils.web_requests_schema_parser.parser import parse
from utils.web_requests_schema_parser.templates import template


@template
@dataclass
class FetchCall:
    function_name: str
    uri: str  # must start with /
    url_parameters: List[str]
    method: str
    attributes: List[str]
    url: str = "http://127.0.0.1:5000/api/v1"
    _template = """
async function $function_name($attributes) {
    let uri = $uri;
    return fetch("$url" + uri, {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: "$method",
        $body
    }).then(res => {
        return res.json();
    });
}
    """

    def attributes_to_str(self):
        return ", ".join(self.url_parameters + self.attributes)

    def body_to_str(self):
        if not self.attributes:
            return ""
        return "body: JSON.stringify({" + ", ".join(f"{a}: {a}" for a in self.attributes) + "})"

    def uri_to_str(self):
        uri = f"\"{self.uri}\""
        if not self.url_parameters:
            return uri
        return uri + "".join(f".replace(\"<{p}>\", {p})" for p in self.url_parameters)


@template
@dataclass
class JsFile:
    functions: List[FetchCall]
    _template = """$functions"""

    def functions_to_str(self):
        return "\n".join(f.to_str() for f in self.functions)


def schema_to_js(text: str) -> str:
    file = parse(text)
    calls = []
    for communication in file.communications:
        new = communication_to_js(communication)
        calls.extend(new)
    file = JsFile(calls)
    code = file.to_str()
    return code


def communication_to_js(communication: Communication) -> List[FetchCall]:
    calls = []
    uri = get_simple_attribute(communication.attributes, "uri", communication.name)
    url_params = url_params_from_uri(uri)
    for req in communication.requests:
        parameters = []
        if req.parameters:
            for attr in req.parameters.attributes:
                parameters.append(attr.name)
        call = FetchCall(f"{str(req.method).lower()}{str(communication.name).title()}",
                         uri, url_params, req.method, parameters)
        calls.append(call)
    return calls
