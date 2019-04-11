function userRegistered() {
  const ajax = new XMLHttpRequest();

  const username = document.querySelector("#username").value;

  ajax.open("POST", "/regcheck", true);

  ajax.onload = function() {
    const registered = JSON.parse(ajax.responseText);
    if (registered.success == false) {
      alert(`Unfortunately this username is already taken`);
      return false;
    }
  };

  const data = new FormData();
  data.append("username", username);

  ajax.send(data);
  return false;
}

var elUsername = document.getElementById("username");
elUsername.addEventListener("blur", userRegistered, false);
