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
