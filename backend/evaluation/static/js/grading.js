class Observable {
    constructor() {
        this.listeners = [];
    }

    updated() {
        for (const listener of this.listeners) {
            listener(this);
        }
    }

    onUpdate(func) {
        this.listeners.push(func);
    }
}

class SubmissionGraduation {

    constructor(submissionId) {
        const testsuiteElements = document.getElementsByClassName(`testsuite-graduation-${submissionId}`);
        this.testsuites = [];
        this.points = 0;
        this.name = submissionId;
        for (const testsuiteElement of testsuiteElements) {
            const testsuiteId = testsuiteElement.id.replace("testsuite-graduation-", "");
            const testsuite = new TestsuiteGraduation(testsuiteId);
            testsuite.onUpdate(this.update.bind(this));
            this.testsuites.push(testsuite);
        }

        const pointsElement = document.getElementById(`submission-points-${submissionId}`);
        this.pointsField = new InputField(pointsElement);

        this.update();
    }

    update() {
        this.points = 0;
        for (const testsuite of this.testsuites) {
            this.points += testsuite.points;
        }
        this.pointsField.setValue(this.points);
    }

    toJSON(_) {
        return {
            name: this.name,
            test_suites: this.testsuites
        }
    }
}

class TestsuiteGraduation extends Observable{

    constructor(testsuiteId) {
        super();
        const testcasesElements = document.getElementsByClassName(`testcase-graduation-${testsuiteId}`);
        this.testcases = [];
        this.comment = "";
        this.points = 0;
        this.name = testsuiteId.split("--")[1];

        for (const testcaseElement of testcasesElements) {
            const testcaseId = testcaseElement.id.replace("graduation-", "");
            const testcase = new TestcaseGraduation(testcaseId);
            testcase.onUpdate(this.update.bind(this));
            this.testcases.push(testcase);
        }

        this.mergedCommentField = document.getElementById(`testsuite-merge-comment-${testsuiteId}`);
        const commentElement = document.getElementById(`testsuite-comment-${testsuiteId}`);
        this.commentField = new InputField(commentElement);
        this.commentField.onUpdate(this.update.bind(this));

        const pointsElement = document.getElementById(`testsuite-points-${testsuiteId}`);
        this.pointsField = new InputField(pointsElement);

        this.update();
    }

    update() {
        this.points = 0;
        for (const testcase of this.testcases) {
            this.points += testcase.points;
        }
        this.pointsField.setValue(this.points);
        this.comment = this.commentField.getValue();

        let mergedComment = "";
        if(this.comment.length > 0) {
            mergedComment += this.comment + "\n\n";
        }
        for (const testcase of this.testcases) {
            const h1 = `${testcase.name}  ${testcase.points}/${testcase.max_points}`
            mergedComment +=  h1 + "\n"
            if(testcase.comment.length > 0) {
                 mergedComment += nChars("=", h1.length) + "\n" +
                    testcase.comment + "\n" +
                    "\n"
            }
        }
        this.mergedCommentField.value = mergedComment;
        this.mergedCommentField.dispatchEvent(new Event("input"));
        this.updated()
    }

    toJSON(_) {
        return {
            name: this.name,
            test_cases: this.testcases
        }
    }
}

class TestcaseGraduation extends Observable {

    constructor(testcaseId) {
        super();
        this.testcaseId = testcaseId;
        this.name = testcaseId.split("--")[2];
        const commentArea = document.getElementById(`comment-${this.testcaseId}`);
        const pointsInput = document.getElementById(`points-${this.testcaseId}`);
        this.max_points = +document.getElementById(`max_points-${this.testcaseId}`).value;
        this.name_field = document.getElementById(`testcase-name-${this.testcaseId}`);

        this.commentField = new InputField(commentArea);
        let fun = field => {
            this.comment = field.getValue();
            this.updated();
        }
        this.commentField.onUpdate(fun.bind(this));
        this.pointsField = new InputField(pointsInput);
        //this.pointsField.field.onchange = this.pointsField.updated.bind(this.pointsField)
        fun = field => {
            this.points = +field.getValue();
            if (this.points === this.max_points) {
                console.log("Same points");
                this.name_field.classList.remove("failed");
                this.name_field.classList.add("passed");
            } else {
                this.name_field.classList.remove("passed");
                this.name_field.classList.add("failed");
            }
            this.updated();
        }
        this.pointsField.onUpdate(fun.bind(this));

        this.comment = this.commentField.getValue();
        this.points = +this.pointsField.getValue();
    }

    toJSON(key) {
        return {
            name: this.name,
            comment: this.comment,
            points: this.points
        }
    }
}

class InputField extends Observable{

    constructor(field) {
        super();
        this.value = field.value;
        this.field = field;
        this.field.oninput = this.updated.bind(this);
    }

    updated() {
        this.value = this.field.value;
        super.updated();
        if (this.field.tagName === "TEXTAREA") {
            checkEnlarge(this.field);
        }
    }

    setValue(v) {
        this.field.value = v;
    }

    getValue() {
        if(this.value === undefined) return ""
        return this.value;
    }
}

const submissions = [];

function init() {
    const submissionElements = document.getElementsByClassName("submission");
    for (const submissionElement of submissionElements) {
        const submissionId = submissionElement.id.replace("submission-", "");
        const submission = new SubmissionGraduation(submissionId);
        submissions.push(submission);
    }

    // Load gradings

}

document.addEventListener("DOMContentLoaded", init);


function nChars(c, n) {
    let v = "";
    for (let i = 0; i < n; i++) {
        v += c;
    }
    return v;
}

async function submitGradings() {
    let data = {
        name: "irrelevant",
        submissions: submissions
    }

    console.log(data);
    const dataToSend = JSON.stringify(data)
    return fetch("/api/grading/update", {
        method: "post",
        headers: {"Content-Type": "application/json"},
        body: dataToSend
    }).then(resp => {
        if (resp.status === 200) {
            return true;
        } else {
            console.log("Status: " + resp.status)
            return false;
        }
    }).catch(err => {
        console.log(err)
        return false;
    })
}


function onSubmitGradingsClick(button, event) {
    event.stopPropagation();
    submitGradings().then(success => {
        if (success) {
            button.style.color = "green";
        } else {
            button.style.color = "red";
        }
    });
}

function onLoadGradingsClick(button, event) {
    event.stopPropagation();
    loadGradings().then(success => {
        if (success) {
            button.style.color = "green";
        } else {
            button.style.color = "red";
        }
    });
}

function loadGradings() {
    return fetch("api/grading/all", {
        method: "GET",
        headers: {"Accept": "application/json"}
    }).then(res => {
        if (res.status === 200) {
            return res.json();
        } else {
            return Promise.reject("cannot load: ");
        }
    }).then(data => {
        for (const submission of data["submissions"]) {
            const submission_id = submission.name;
            for(const testsuite of submission["test_suites"]){
                const testsuite_id = `${submission_id}--${testsuite.name}`;
                for(const testcase of testsuite["test_cases"]) {
                    const testcase_id = `${testsuite_id}--${testcase.name}`;
                    const commentArea = document.getElementById(`comment-${testcase_id}`);
                    const pointsInput = document.getElementById(`points-${testcase_id}`);

                    if (commentArea != null) {
                        commentArea.value = testcase.comment;
                        commentArea.dispatchEvent(new Event("input"));
                    }
                    if (pointsInput != null) {
                        pointsInput.value = testcase.points;
                        pointsInput.dispatchEvent(new Event("input"));
                    }
                }
            }
        }
        return true;
    }).catch(e => {
        console.error(e);
        return false;
    })
}

function copyComment(testsuite_id) {
    let mergeComment = document.getElementById(`testsuite-merge-comment-${testsuite_id}`);
    mergeComment.select();
    document.execCommand("copy");
    console.log("copied: " + mergeComment.value)
}

function startCopying() {
    const comments = document.getElementsByClassName("merge-comment");
    for (const comment of comments) {
        comment.disabled = false;
        comment.dispatchEvent(new Event("input"));
    }
    const buttons = document.getElementsByClassName("btnCopyMergeComment");
    for (const button of buttons) {
        button.disabled = false;
    }
}
