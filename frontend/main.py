from flask import Flask, request, render_template, render_template_string, redirect
from schema_classes.tools_schema import PrepareRequestBase, PreparePOST400Response, PreparePOST200Response
from schema_classes.overview_schema import OverviewRequestBase, OverviewGET200Response

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


@app.route("/correction/<student>", methods=['GET'])
def correction(student):
    student_num = int(student)
    reports = [{
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
                "bookmarked": False,
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
        }, {
            "name": "Task 2"
        }]
    }, {
        "name": "Another"
    }]
    if student_num < 0:
        return redirect("/correction/" + str(len(reports)-1))
    if student_num >= len(reports):
        return redirect("/correction/" + str(0))
    return render_template("correction.jinja2", report=reports[student_num], current_num=student_num)


@app.route("/list")
def exam_list():

    var2 = {
        "name": "Vincent",
        "passed": False,
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


@app.route("/list")
def exam_list_header():
    res, err = OverviewRequestBase.get()
    if isinstance(res, OverviewGET200Response):
        return render_template("list.jinja2", reports=res)


if __name__ == '__main__':
    app.run(port=5001)