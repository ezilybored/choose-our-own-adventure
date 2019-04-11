function checkPassword(e) {
  var submit = document.getElementById("submit");
  submit.disabled = false;
  var elMsg = document.getElementById("feedback");
  if (this.value.length < 5) {
    elMsg.textContent = "Password must be at least 5 characters or more!";
    submit.disabled = true;
  } else if (this.value.length > 20) {
    elMsg.textContent = "Password must be less than least 20 characters!";
    submit.disabled = true;
  } else if (this.value.search(/\d/) == -1) {
    elMsg.textContent = "Password must contain at least one number!";
    submit.disabled = true;
  } else {
    elMsg.textContent = "";
  }
}

function checkConfirm(e) {
  var submit = document.getElementById("submit");
  submit.disabled = false;
  var elPassword = document.getElementById("password");
  var elMsg = document.getElementById("feedback");
  if (this.value !== elPassword.value) {
    elMsg.textContent = "Password fields must match";
    submit.disabled = true;
  } else {
    elMsg.textContent = "";
    return;
  }
}

var elPassword = document.getElementById("password");
elPassword.addEventListener("blur", checkPassword, false);

var elcheck = document.getElementById("confirm");
elcheck.addEventListener("blur", checkConfirm, false);
