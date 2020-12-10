from flask import request


def api(request_type):
    def inner(func):
        def wrapper(*_, **__):
            data = request_type.from_dict(request.get_json())
            res = func(data)
            return res.to_json()

        return wrapper

    return inner
