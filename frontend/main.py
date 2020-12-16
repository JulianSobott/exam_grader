from flask import Flask, request, render_template, render_template_string
from schema_classes import PrepareRequestBase, PreparePOST400Response, PreparePOST200Response

app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
def file_picker():
    if request.method == 'POST':
        path = request.form["path"]
        # if path is empty
        if path or path == "":
            return render_template("selector.jinja2", text="filepath", status="Filepath must be specified!")
        # FIXME missing parameter
        # var, err = PrepareRequestBase.post(path)
        # if err:
        #     text = err
        # else:
        #     if isinstance(var, PreparePOST200Response):
        #         text = var.file_errors
        #     elif isinstance(var, PreparePOST400Response):
        #         text = var.error
        #     else:
        #         text = var
        return render_template("selector.jinja2", text=path, status=path)
    else:
        return render_template("selector.jinja2", text="filepath")


@app.route("/correction")
def correction():
    var = {
        "name": "Sebastian",
        "students_number": 81194,
        "num_correct_subtasks": 2,
        "num_subtasks": 4,
        "points": 99,
        "max_points": 100,
        "step_failed": "Error 404",
        "tasks": [{
            "name": "Task 1",
            "points": 3,
            "max_points": 5,
            "bookmarked": True,
            "sub_tasks": [{
                "name": "Subtask 1",
                "description": "The task is to do this and that",
                "points": 3.5,
                "max_points": 5,
                "bookmarked": True,
                "code_snippets": [{
                    "name": "Snippet 1",
                    "class_name": "ClassTester.java",
                    "found": True,
                    "code": "This is the code for the task"
                }],
                "testcases": [{
                    "name": "Assertion 1",
                    "passed": False,
                    "assertion": "The assertion to be passed"
                }]
            }, {
                "name": "Subtask 2",
                "description": "The task is to do this and that",
                "points": 3.5,
                "max_points": 5,
                "bookmarked": True,
                "code_snippets": [{
                    "name": "Snippet 1",
                    "class_name": "ClassTester.java",
                    "found": True,
                    "code": "This is the code for the task"
                }],
                "testcases": [{
                    "name": "Assertion 1",
                    "passed": False,
                    "assertion": "The assertion to be passed"
                }]
            }]
        }]
    }
    return render_template("correction.jinja2", report=var)


@app.route("/list")
def exam_list():
    dummy = [{
        "name": "Student 1",
        "passed": True,
        "points": 30
    }, {
        "name": "Student 2",
        "passed": False,
        "points": 2
    }]

    return render_template("list.jinja2", reports=dummy)


if __name__ == '__main__':
    app.run(port=5001)