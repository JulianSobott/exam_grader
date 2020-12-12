# TODO work here

from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route("/")
def p():
    var = requests.post("http://127.0.0.1:5000/api/v1/tools/prepare", data={"zip_url": ""}).text
    return render_template("index.html", name=var)

if __name__ == '__main__':
    app.run(port=5001)