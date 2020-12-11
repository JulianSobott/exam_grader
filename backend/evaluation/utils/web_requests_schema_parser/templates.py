class CharStream:

    def __init__(self, chars: str):
        self.chars = chars
        self.idx = 0

    def peek(self):
        if len(self.chars) <= self.idx:
            return False
        return self.chars[self.idx]

    def prev(self):
        if self.idx == 0:
            return ""
        return self.chars[self.idx - 1]

    def has_next(self):
        return self.idx < len(self.chars)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.chars[self.idx]
        except IndexError:
            raise StopIteration
        finally:
            self.idx += 1

    def __repr__(self):
        if len(self.chars) <= self.idx:
            return self.chars + "||"
        return self.chars[:self.idx] + "|" + self.chars[self.idx] + "|" + self.chars[self.idx + 1:]


delta_table = {
    "DEFAULT": {
        "CHAR": "DEFAULT", "WHITESPACE": "DEFAULT", "BEGIN": "VAR", "NEWLINE": "LINE_BEGIN", "OTHER": "DEFAULT"
    },
    "LINE_BEGIN": {
        "CHAR": "DEFAULT", "WHITESPACE": "INDENT", "BEGIN": "VAR", "NEWLINE": "LINE_BEGIN", "OTHER": "DEFAULT"
    },
    "INDENT": {
        "CHAR": "DEFAULT", "WHITESPACE": "INDENT", "BEGIN": "VAR", "NEWLINE": "LINE_BEGIN", "OTHER": "DEFAULT"
    },
    "VAR": {
        "CHAR": "VAR", "WHITESPACE": "DEFAULT", "BEGIN": "ERROR", "NEWLINE": "LINE_BEGIN", "OTHER": "DEFAULT"
    }
}


class Template:

    def __init__(self):
        self._template = None

    def to_str(self):

        def token_var(cs: CharStream) -> str:
            var = ""
            cs.__next__()  # skip var sign
            while cs.has_next():
                c = cs.peek()
                if get_char_class(c) == "CHAR":
                    var += c
                    cs.__next__()
                else:
                    break
            return var

        def token_text(cs: CharStream) -> str:
            text = cs.__next__()
            while cs.has_next():
                c = cs.peek()
                if get_char_class(c) in ["CHAR", "WHITESPACE", "OTHER"]:
                    text += c
                    cs.__next__()
                else:
                    break
            return text

        def token_indent(cs: CharStream) -> str:
            text = ""
            while cs.has_next():
                c = cs.peek()
                if get_char_class(c) in ["WHITESPACE"]:
                    text += c
                    cs.__next__()
                else:
                    break
            return text

        out = ""
        indent = ""
        state = "LINE_BEGIN"
        cs = CharStream(self._template)
        while cs.has_next():
            if get_char_class(cs.peek()) == "NEWLINE":
                out += cs.__next__()
                indent = ""
            if state == "DEFAULT":
                text = token_text(cs)
                out += text
            if state == "VAR":
                name = token_var(cs)
                out += self.substitude(name, indent)
            if state == "INDENT":
                indent = token_indent(cs)
            if cs.has_next():
                char_class = get_char_class(cs.peek())
                new_state = delta_table[state][char_class]
                if new_state == "ERROR":
                    print("ERROR: " + state + " " + repr(cs))
                    return "ERROR"
                state = new_state
        return out

    def substitude(self, var_name, indentation):
        try:
            text = self.__getattribute__(f"{var_name}_to_str")()
        except AttributeError:
            attribute = self.__getattribute__(var_name)
            text = self.sub(attribute)
        lines = text.split("\n")
        text = "\n".join(indentation + l for l in lines)
        return text

    def sub(self, value):
        """no indentation, just to string"""
        if value is None:
            return ""
        if isinstance(value, Template):
            return value.to_str()
        elif isinstance(value, list):
            return "\n".join(self.sub(v) for v in value)
        else:
            return str(value)


def get_char_class(c: str):
    if c == "$":
        return "BEGIN"
    if c in " \t":
        return "WHITESPACE"
    if c in ["\n", "\r\n"]:
        return "NEWLINE"
    if c.isidentifier():
        return "CHAR"
    return "OTHER"
