from typing import List

from lark import Lark, Tree
from lark.indenter import Indenter

# TODO: typedef maybe also reference in json schema

grammar = r"""
    COMMENT: "#" /[^\n]/*
    PRIMITIVE.2: "str" | "int" | "float" | "object"
    TYPEDEF.2: "typedef"
    REQUEST: "->"
    RESPONSE: "<-"
    SEPARATOR: ":"
    OPTIONAL: "?"
    ARRAY: "[]"
    IDENTIFIER: /[a-zA-Z][a-zA-Z0-9_]*/
    
    ?start          : _NL* block*
    block           : communication _NL*
                    | typedef _NL*
    communication   : IDENTIFIER _NL _INDENT  request response _DEDENT
    request         : REQUEST _NL body?
    response        : RESPONSE _NL body?
    body            : _INDENT object* _DEDENT
    object          : OPTIONAL? IDENTIFIER ARRAY? SEPARATOR type _NL [attributes]
    type            : PRIMITIVE | enum | global_type
    enum            : IDENTIFIER ("," IDENTIFIER)*
    global_type     : "$" IDENTIFIER
    attributes      : body
    
    typedef         : TYPEDEF IDENTIFIER _NL body
    
    %declare _INDENT _DEDENT
    
    _NL: /(\r?\n[\t ]*)+/
    
    %import common.WS_INLINE
    %ignore WS_INLINE
    %ignore COMMENT
"""


class GrammarIndenter(Indenter):
    NL_type = "_NL"
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4


example = """

typedef my_type
    val1: str
    val2: int
    val3: object
        inner: int

prepare
    ->
        ?hello[]: $my_type   # this is optional
            val1: str
            val2: NOT_VALID, INVALID2
        other: ENUM1, ENUM2
        obj: object
            attr1: int
            attr2: str
        arr[]: int
    <-
       world: str
# comment
another
    -> 
        val: int
    <-
"""


def parse(text: str):
    parser = Lark(grammar, parser="lalr", postlex=GrammarIndenter())
    return parser.parse(text)


def schema_to_python(text: str):
    pass


def schema_to_json_schemas(text: str) -> List[dict]:
    types = {}

    def typedef(node: Tree):
        name = node.children[1]
        body_node = node.children[2]
        types[name] = body_node

    def communication(node: Tree):
        name = node.children[0]
        request_schema = req_resp(node.children[1], name, "Request")
        response_schema = req_resp(node.children[2], name, "Response")
        return {
            "name": name,
            "request": request_schema,
            "response": response_schema,
        }

    def req_resp(node: Tree, name: str, prefix: str):
        json_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "title": f"{name}_{prefix}",
            "properties": {},
            "required": []
        }
        if len(node.children) > 1:
            required, properties = body(node.children[1])
            json_schema["properties"] = properties
            json_schema["required"] = required
        return json_schema

    def body(node: Tree):
        required_props = []
        properties = {}
        for obj in node.children:
            required, prop = object_declaration(obj)
            properties.update(prop)
            if required:
                required_props.append(list(prop.keys())[0])
        return required_props, properties

    def object_type(prop_type: dict, body_node: Tree):
        required, properties = body(body_node)
        prop_type["properties"] = properties
        prop_type["required"] = required

    def object_declaration(node: Tree):
        type_mapping = {"str": "string", "float": "number", "int": "integer", "bool": "boolean", "object": "object"}
        required = True
        idx = 0
        if node.children[0] == "?":  # Optional
            required = False
            idx = 1
        name = node.children[idx]
        is_array = False
        if node.children[idx + 1] == "[]":
            is_array = True
            idx += 1
        obj_type_gen = node.children[idx + 2].children[0]  # skip SEPARATOR
        if isinstance(obj_type_gen, str):  # primitive
            prop_type = {
                "type": type_mapping[str(obj_type_gen)]
            }
            if obj_type_gen == "object":
                object_type(prop_type, node.children[idx + 3].children[0])
        elif obj_type_gen.data == "global_type":
            name = obj_type_gen.children[0]
            prop_type = {
                "type": "object"
            }
            if name not in types:
                raise ReferenceError(f"No typedef with name: {name}")
            object_type(prop_type, types[name])
        else:  # enum
            prop_type = {
                "type": type_mapping["str"],
                "enum": [str(token) for token in obj_type_gen.children]
            }
        if is_array:
            prop = {
                name: {
                    "type": "array",
                    "items": prop_type
                }
            }
        else:
            prop = {
                name: prop_type
            }
        return required, prop

    ast = parse(text)
    schemas = []
    for block_node in ast.children:
        n = block_node.children[0]
        if n.data == "communication":
            communication_schemas = communication(n)
            schemas.append(communication_schemas)
        elif n.data == "typedef":
            typedef(n)
    return schemas


if __name__ == '__main__':
    parse(example)
    schema_to_json_schemas(example)
