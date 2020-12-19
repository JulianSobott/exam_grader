// later: add keyboard-shortcuts

// toggle bookmark submission, task or subtask
    // id = origin of the button click
    // bookmark = current status of boolean bookmark
function bookmarkClick(id) {
    // convert bookmark String to JS-boolean
    const element = document.getElementById(`bookmark-${id}`);
    const old_bookmark = element.getAttribute("is-bookmarked") === "true";
    const new_bookmark = !old_bookmark;
    // split into id-sections (submission, task, subtask)
    let elements = id.split("--")
    console.log(elements);
    // update toggled bookmark at server and show response
    postBookmark({elements: elements}, new_bookmark).then(res => {
        if (res.status_code === 200) {
            element.setAttribute("is-bookmarked", `${new_bookmark}`)
        } else {
            console.log(res.error.err_msg)
        }
    })
}

// when input changes: post points to server
    // name_id = html-id of the origin input
    // (must be striped before processing)
function set_points(name_id) {
    // split into id-sections (submission, task, subtask)
    let elements = name_id.split("__")[1].split("--")
    console.log(elements)
    // get points from input field
    let points = parseFloat(document.getElementById(name_id).value);
    // post points to server and show response
    postPoints({elements: elements}, points).then(res => {
        console.log(res.status_code)
        if (res.status_code === 200) {
            console.log(name_id + ": " + points);
        }
        else {
            console.error(res.error.err_msg);
        }
    })
}

function max_point(name_id) {
    let max = document.getElementById(name_id).getAttribute("max");
     document.getElementById(name_id).setAttribute("value", max);
     set_points(name_id);
}

// when input changes: post comment to server
    // name_id = html-id of the origin input
    // (must be striped before processing)
function set_comment(name_id) {
    // split into id-sections (submission, task, subtask)
    let elements = name_id.split("__")[1].split("--")
    console.log(elements)
    // get comment from input field
    let comment = document.getElementById(name_id).value;
    // post comment to server and show response
    postComment({elements: elements}, comment).then(res => {
        console.log(res.status_code)
        if (res.status_code === 200) {
            console.log(name_id + ": " + comment);
        }
        else if (res.status_code === 404) {
            console.log(res.err_msg)
        }
        else {
            console.error(res.error.err_msg);
        }
    })
}

// set submission status to DONE
function finish(id) {
    // post status to server and show response
    postStatus({elements: [id]}, "DONE").then(res => {
        console.log(res.status_code)
        if (res.status_code === 200) {
            console.log("status: DONE")
        }
        else {
            console.error(res.error.err_msg);
        }
    })
}

// set submission status to ACTIVE
    // also used to set the status from NOT_STARED to ACTIVE
function unfinish(id) {
    // post status to server and show response
     postStatus({elements: [id]}, "ACTIVE").then(res => {
        console.log(res.status_code)
         if (res.status_code === 200) {
            console.log("status: ACTIVE")
        }
        else {
            console.error(res.error.err_msg);
        }
    })
}