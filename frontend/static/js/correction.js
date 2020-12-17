// later: add keyboard-shortcuts
var url_base = "http://localhost:5000//api/v1"

function bookmarkClick(id) {
    console.log(id)
    var url = url_base + "/grading/bookmark";
    var param = "identifier=   &bookmarked=" + true;
    var request = new XMLHttpRequest();
    request.open("POST", url, true);
    request.setRequestHeader("Bookmark", "/correction");
    request.send(param);
}

function set_points(name_id) {
    var points = document.getElementById(name_id).value;
    var url = url_base + "/grading/points"
    var params = "identifier=   &points=" + points;
    var request = new XMLHttpRequest();
    request.open("POST", url, true);
    request.setRequestHeader("Points", "/correction");
    request.send(params);
    console.log(name_id + ": " + points);
}

function set_comment(name_id) {
    var comment = document.getElementById(name_id).value;
    var url = url_base + "/grading/comment"
    var params = "identifier=   &comment=" + comment;
    var request = new XMLHttpRequest();
    request.open("POST", url, true);
    request.setRequestHeader("Comment", "/correction");
    request.send(params);
    console.log(name_id + ": " + comment);
}

document.getElementById("finish_link").addEventListener("click", function finish() {
    console.log("Finish")
    var url = url_base + "/grading/status"
    var status = "identifier=   &status=DONE";
    var request = new XMLHttpRequest();
    request.open("POST", url, true);
    request.setRequestHeader("Finish", "/correction");
    request.send(status);
});

document.getElementById("unfinish_link").addEventListener("click", function unfinish() {
    console.log("Unfinish")
    var url = url_base + "/grading/status"
    var status = "identifier=   &points=ACTIVE";
    var request = new XMLHttpRequest();
    request.open("POST", url, true);
    request.setRequestHeader("Unfinish", "/correction");
    request.send(status);
});