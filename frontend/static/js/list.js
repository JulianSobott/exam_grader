let show_classes = new Set([
    "bookmarked_True",
    "bookmarked_False",
    "status_NOT_STARTED",
    "status_ACTIVE",
    "status_DONE",
    "passed_True",
    "passed_False"
])


function filter_click(id, add) {
    let checkBox = document.getElementById(id);
    if (checkBox.checked === true) {
        show_classes.add(add);
    } else {
        show_classes.delete(add);
    }
    applyFilter();
}

function applyFilter() {
    let slides = document.getElementsByClassName("slide-wrapper");
    for (const slide of slides) {
        slide.style.display = "none";
    }
    for (const showClass of show_classes) {
        const elements = document.getElementsByClassName(showClass);
        for (const element of elements) {
            element.style.display = "block";
        }
    }
}

// submit all reports to the canvas api
function submit() {
    postSubmit_To_Canvas().then(res => {
        if (res.status_code === 200) {
            console.log("submitted successfully")
        }
        else if (res.status_code === 500) {
            console.log(res.err_msg)
        }
    })
}