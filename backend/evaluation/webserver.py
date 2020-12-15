from flask import Flask
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
            get("/overview", api.overview.OverviewRequest),
            group(
                "/grading",
                get("/submissions/<submission_name>", api.grading.SubmissionsRequest),
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


@app.route("/test/<name>")
def p(name):
    return "Hello " + name


if __name__ == '__main__':
    app.run(port=5000)
