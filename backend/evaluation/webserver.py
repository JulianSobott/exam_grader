from flask import Flask, request
from flask_cors import CORS

import api
from utils.web_routing import routes, group, get, post

app = Flask(__name__)
CORS(app)


routes(
    app,
    group(
        "/api",
        group(
            "/v1",
            group(
                "/tools",
                post("/prepare", api.tools.PrepareRequest),
                post("/rename_and_fill", api.tools.RenameAndFillRequest),
                get("/test_files", api.tools.TestFilesRequest),
            ),
            group(
                "/grading",
                get("/<submission_name>", api.todo),
                group(
                    "/<submission_name>",
                    post("/points", api.todo),
                    post("/comment", api.todo),
                    post("/bookmark", api.todo)
                )
            ),
            group(
                "/statistics",
                get("", api.todo)
            )
        )
    )
)


@app.route("/")
def p():
    return "Hello"
