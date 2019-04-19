function manage(e) {
  var submit = document.getElementById("submit");
  var elements = document.getElementsByTagName("input");

  for (i = 0; i < elements.length; i++) {
    if (elements[i].type == ("text" || "password") && elements[i].value == "") {
      submit.disabled = true;
      return false;
    } else {
      submit.disabled = false;
    }
  }
}

var eventAddition = document.getElementsByTagName("input");
for (i = 0; i < eventAddition.length; i++) {
  eventAddition[i].addEventListener("blur", manage, false);
}
