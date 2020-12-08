from dataclasses import dataclass
from typing import Callable, List, Union

from flask import Flask, render_template, request, Response
from sassutils.wsgi import SassMiddleware

from common import gradings_file, submission_folder, logger, submission_names
from get_code import get_full_class
from reporting import create_report
from schema_classes import Gradings
from utils.web_routing import routes, group, get, post
import api

app = Flask(__name__)

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
                post("/prepare", api.todo),
                post("/rename", api.todo),
                post("/add_empty", api.todo),
                post("/test", api.todo),
            )
        )
    )
)

#
# @app.route("/", methods=["GET"])
# def index():
#     report, err = create_report()
#     if err:
#         return f"<pre>Error:\n{err}<pre>"
#     return render_template("test_report_all.html", report=report)
#
#
# @app.route("/api/grading/update", methods=["POST"])
# def update_grading():
#     gradings = Gradings.from_json(request.data)
#     with open(gradings_file, "w") as f:
#         f.write(gradings.to_json())
#     return {"status": "success"}
#
#
# @app.route("/api/grading/all", methods=["GET"])
# def get_grading():
#     with open(gradings_file, "r") as f:
#         return Response(f.read(), headers={"Content-Type": "application/json"})
#
#
# @app.route("/<submission_name>/<testsuite_name>.java")
# def java_class(submission_name: str = None, testsuite_name: str = None):
#     submission_path = submission_folder.joinpath(submission_name)
#     code, status = get_full_class(submission_path, testsuite_name)
#     code = f"/*{status}*/\n{code}"
#     return code
#
#
# @app.route("/<matrikel_number>")
# def get_submission(matrikel_number=None):
#     logger.debug(f"Serve submission: {matrikel_number}")
#     found_names = submission_names([matrikel_number])
#     if found_names:
#         report, err = create_report(found_names)
#         if err:
#             return f"<pre>Error:\n{err}<pre>"
#     else:
#         return f"No submission with found for: {matrikel_number}"
#     return render_template("test_report_all.html", report=report)
