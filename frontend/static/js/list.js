
function filter_bookmark_click() {
    let checkBox = document.getElementById("cb_bookmarked");
  let bookmarked_elements = document.getElementsByClassName("bookmarked_True");
  let not_bookmarked_elements = document.getElementsByClassName("bookmarked_False")
  if (checkBox.checked === true){
    for (const notBookmarkedElement of not_bookmarked_elements) {
        notBookmarkedElement.style.display = "none";
    }
      for (const element of bookmarked_elements) {
          element.style.display = "block";
      }
  } else {
     for (const notBookmarkedElement of not_bookmarked_elements) {
        notBookmarkedElement.style.display = "block";
    }
      for (const element of bookmarked_elements) {
          element.style.display = "block";
      }
  }
}

function init() {
  let checkBox = document.getElementById("cb_bookmarked");
  checkBox.addEventListener("click", filter_bookmark_click);
}

window.addEventListener("DOMContentLoaded", init);
