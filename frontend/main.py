# TODO work here

from flask import Flask, render_template

from schema_classes import PrepareRequestBase, PreparePOST400Response, PreparePOST200Response

app = Flask(__name__)


@app.route("/")
def p():
    var, err = PrepareRequestBase.post("/path/that/does/not/exist")
    if err:
        text = err
    else:
        if isinstance(var, PreparePOST200Response):
            text = var.file_errors
        elif isinstance(var, PreparePOST400Response):
            text = var.error
        else:
            text = var
    return render_template("index.html", name=text)


if __name__ == '__main__':
    app.run(port=5001)