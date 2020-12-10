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
                "/start_page",
                get("/state", api.start_page.state)
            ),
            group(
                "/overview",
                get("/data", api.overview.data)
            ),
            group(
                "/tools",
                post("/prepare", api.tools.prepare),
                post("/rename", api.todo),
                post("/add_empty", api.todo),
                post("/test", api.todo),
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


@app.route("/login", methods=["GET"])
def p():
    req = request.get_json()
