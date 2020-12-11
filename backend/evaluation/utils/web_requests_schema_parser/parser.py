from typing import List

from lark import Lark, Tree, Token
from lark.indenter import Indenter


# TODO: typedef maybe also reference in json schema
# TODO: typedef also other types
# TODO: other types: bodies


class GrammarIndenter(Indenter):
    NL_type = "_NL"
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 4


class MyIndenter:
    """_NL _INDENT/_DEDENT to BEGIN and END tokens"""

    BEGIN_type = "_BEGIN"
    END_type = "_END"

    def __init__(self):
        self.pre_lexer = GrammarIndenter()

    def handle_NL(self, token):
        yield token

    def _process(self, stream):
        for token in self.pre_lexer.process(stream):
            if token.type == self.pre_lexer.NL_type:
                continue
            elif token.type == self.pre_lexer.INDENT_type:
                yield Token.new_borrow_pos(self.BEGIN_type, token.value, token)
            elif token.type == self.pre_lexer.DEDENT_type:
                yield Token.new_borrow_pos(self.END_type, token.value, token)
            else:
                yield token

    def process(self, stream):
        return self._process(stream)

    # XXX Hack for ContextualLexer. Maybe there's a more elegant solution?
    @property
    def always_accept(self):
        return self.pre_lexer.always_accept


example = """

typedef object my_type
    val1: str
    val2: int
    val3: object AnotherType
        inner: int

prepare
    ->
        GET
            ?hello[]: $my_type   # this is optional
            val1: str
            val2: NOT_VALID, INVALID2
            other: ENUM1, ENUM2
            obj: object B
                attr1: int
                attr2: str
            arr[]: int
    <-
       world: str
# comment
another
    -> 
        GET
            val: int
    <-
"""


def parse(text: str):
    parser = Lark.open("grammar.lark", parser="lalr", postlex=MyIndenter())
    return parser.parse(text)


def schema_to_python(text: str):
    pass


def schema_to_json_schemas(text: str) -> List[dict]:
    types = {}
    required_types = set()

    def typedef(node: Tree):
        type_name = str(node.children[1].children[0])  # TODO only objects are possible yet
        name = str(node.children[1].children[1])
        body_node = node.children[2]
        types[name] = body_node

    def communication(node: Tree):
        name = str(node.children[0])
        request_schema = req_resp(node.children[1], name, "Request")
        response_schema = req_resp(node.children[2], name, "Response")
        return {
            "name": name,
            "request": request_schema,
            "response": response_schema,
        }

    def req_resp(node: Tree, name: str, prefix: str):
        required_types.clear()
        json_schema = {
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "title": f"{name}_{prefix}",
            "properties": {},
            "definitions": {},
            "required": []
        }
        if len(node.children) > 1:
            required, properties = body(node.children[1])
            json_schema["properties"] = properties
            json_schema["required"] = required
            for definition in required_types:
                if definition not in types:
                    raise ReferenceError(f"No typedef with name: {definition}")
                prop_type = {
                    "type": "object",
                    "title": definition
                }
                object_type(prop_type, types[definition])
                json_schema["definitions"][definition] = prop_type
        return json_schema

    def body(node: Tree):
        required_props = []
        properties = {}
        for obj in node.children:
            required, prop = attribute(obj)
            properties.update(prop)
            if required:
                required_props.append(list(prop.keys())[0])
        return required_props, properties

    def object_type(prop_type: dict, body_node: Tree):
        required, properties = body(body_node)
        prop_type["properties"] = properties
        prop_type["required"] = required

    def attribute(node: Tree):
        type_mapping = {"str": "string", "float": "number", "int": "integer", "bool": "boolean"}
        required = True
        idx = 0
        if node.children[0] == "?":  # Optional
            required = False
            idx = 1
        name = str(node.children[idx])
        is_array = False
        if node.children[idx + 1] == "[]":
            is_array = True
            idx += 1
        obj_type_gen = node.children[idx + 2].children[0]  # skip SEPARATOR
        if isinstance(obj_type_gen, str):  # primitive
            prop_type = {
                "type": type_mapping[str(obj_type_gen)]
            }
        elif obj_type_gen.data == "global_type":
            glob_name = str(obj_type_gen.children[0])
            required_types.add(glob_name)
            prop_type = {
                "$ref": f"#/definitions/{glob_name}"
            }
        elif obj_type_gen.data == "enum":
            prop_type = {
                "type": type_mapping["str"],
                "title": str(node.children[0]),  # attribute key is title
                "enum": [str(token) for token in obj_type_gen.children]
            }
        elif obj_type_gen.data == "object":
            prop_type = {
                "type": "object",
                "title": str(obj_type_gen.children[1])
            }
            object_type(prop_type, node.children[idx + 3])
        else:
            raise TypeError("Unknown type: " + str(obj_type_gen))
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
    import json

    parse(example)
    print(json.dumps(schema_to_json_schemas(example), indent=2))
