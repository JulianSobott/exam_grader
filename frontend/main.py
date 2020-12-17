# TODO work here

from flask import Flask, render_template, render_template_string

# from schema_classes import PrepareRequestBase, PreparePOST400Response, PreparePOST200Response

app = Flask(__name__)


# @app.route("/dummy")
# def dummy():
#     var, err = PrepareRequestBase.post("/path/that/does/not/exist")
#     if err:
#         text = err
#     else:
#         if isinstance(var, PreparePOST200Response):
#             text = var.file_errors
#         elif isinstance(var, PreparePOST400Response):
#             text = var.error
#         else:
#             text = var
#     return render_template_string("{{ name }}", name=text)


@app.route("/")
def selctor():
    return render_template("selector.jinja2")


# def file_picker():
#     var, err = PrepareRequestBase.post("/path/that/does/not/exist")
#     if err:
#         text = err
#     else:
#         if isinstance(var, PreparePOST200Response):
#             text = var.file_errors
#         elif isinstance(var, PreparePOST400Response):
#             text = var.error
#         else:
#             text = var
#     return render_template("correction.jinja2", name=text)


@app.route("/correction")
def correction():
    var = {
        "name": "Sebastian",
        "matrikel": 81194,
        "tested": 3,
        "success": 2,
        "failed": 1
    }
    return render_template("correction.jinja2", var=var)


@app.route("/list")
def exam_list():
    var2 = {
        "name": "Vincent",
        "passed": True,
        "points": 45,
        "max_points": 50,
        "bookmark": True,
        "status": "angefangen"
    }
    var3 = {
        "name": "Julian",
        "passed": True,
        "points": 50,
        "max_points": 50,
        "bookmark": False,
        "status": "unbearbeitet"
    }
    dummy = [var2, var3]
    return render_template("list.jinja2", reports=dummy)


if __name__ == '__main__':
    app.run(port=5001)