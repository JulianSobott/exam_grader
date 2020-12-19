from flask import Flask, request, render_template, render_template_string, redirect
from schema_classes.tools_schema import PrepareRequestBase, PreparePOST400Response, PreparePOST200Response
from schema_classes.overview_schema import OverviewRequestBase, OverviewGET200Response
from schema_classes.grading_schema import *

app = Flask(__name__)


@app.route("/", methods=['POST', 'GET'])
# select the filepath to the submission folder
def file_picker():
    if request.method == 'POST':
        path = request.form["path"]
        # if path is empty
        if path is None or path == "":
            return render_template("selector.jinja2", text="filepath", status="Filepath must be specified!")
        var, err = PrepareRequestBase.post(path)
        if err:
            text = err
        else:
            if isinstance(var, PreparePOST200Response):
                text = var.file_errors
            elif isinstance(var, PreparePOST400Response):
                text = var.error
            else:
                text = var
        return render_template("selector.jinja2", text=path, status=text)
    else:
        return render_template("selector.jinja2", text="filepath")


@app.route("/correction/<student>", methods=['GET'])
# the correction view for 1 submission
def correction(student):
    student_num = int(student)
    try:
        # fetch submitted exam nameso
        res, err = OverviewRequestBase.get()
        if isinstance(res, OverviewGET200Response):
            res = res.submissions

            # nex and previous buttons will loop
            if student_num < 0:
                return redirect("/correction/" + str(len(res) - 1))
            if student_num >= len(res):
                return redirect("/correction/" + str(0))

            # fetch data for specific submission
            report, err = SubmissionsRequestBase.get(res[student_num].submission_id)
            if isinstance(report, SubmissionsGET200Response):
                return render_template("correction.jinja2", report=report.submission, current_num=student_num)
            elif isinstance(report, SubmissionsGET404Response) or isinstance(report, SubmissionsGET500Response):
                print("Error " + str(report.status_code) + ":\t" + report.err_msg)
                app.logger("Error " + str(report.status_code) + ":\t" + report.err_msg)
    except Exception as e:
        print("Error: " + str(e))


@app.route("/list")
def exam_list_header():
    try:
        res, err = OverviewRequestBase.get()
        if isinstance(res, OverviewGET200Response):
            return render_template("list.jinja2", reports=res)
    except Exception as e:
        print("Error: " + str(e))


if __name__ == '__main__':
    app.run(port=5001)
