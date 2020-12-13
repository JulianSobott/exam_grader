document.getElementById("list").addEventListener("click", goto_list);

function goto_list() {
    window.open(document.URL, '/list.jinja2');
}