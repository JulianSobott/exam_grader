function expand(element) {
    let sibling = element.nextElementSibling;
    while (!sibling.classList.contains("expandable-container") && sibling !== element) {
        sibling = sibling.nextElementSibling;
    }
    if (sibling.classList.contains("expandable-container")) {
        if (sibling.classList.contains("open")) {
            sibling.classList.add("close");
            sibling.classList.remove("open")
        } else {
            sibling.classList.add("open")
            sibling.classList.remove("close")
        }
    }
}

function showFullClassCode(testsuite_id) {
    event.stopPropagation();
    const split = testsuite_id.split("--");
    const submission_name = split[0];
    const testsuite_name = split[1];
    const class_name = testsuite_name.replace("Test", "");
    const codeElement = document.getElementById("code-" + testsuite_id);
    if (codeElement.innerHTML.length > 0) {
        if (codeElement.parentElement.style.display === "none") {
            codeElement.parentElement.style.display = "block";
        } else {
            codeElement.parentElement.style.display = "none";
        }
        return;
    }
    fetch(`/${submission_name}/${class_name}.java`, {
        method: "get"
    }).then(res => {
        if (res.status === 200) {
            // Class code
            return res.text();
        } else {
            console.error("Class not found: " + res.url)
            return Promise.reject("file not found");
        }
    }).then(classText => {
        codeElement.innerHTML = classText;
        codeElement.parentElement.style.display = "block";
        Prism.highlightElement(codeElement);
    }).catch(reason => {
        console.error(reason);
    });

}

function checkEnlarge(textarea) {
    textarea.style.height = "auto";
    textarea.style.height = textarea.scrollHeight + "px";
}

function toggleGraduationVisibility(event, cb) {
    for (let e of document.getElementsByClassName("graduation")) {
        e.style.display = cb.checked ? "flex" : "none";
    }
    event.stopPropagation();
}

function init() {
    collapse_all();
}

function collapse_all() {
    let containers = document.getElementsByClassName("expandable-container");
    for (let container of containers) {
        if (!container.classList.contains("manual")) {
            let passed = container.parentElement.classList.contains("container-passed")
            // TODO:
            if (passed || true) {
                container.classList.add("close")
            } else {
                container.classList.add("open")
            }
        } else {
            container.classList.add("close")
        }
    }
}


document.onreadystatechange = init