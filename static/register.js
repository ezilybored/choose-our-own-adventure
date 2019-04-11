(function() {
  var form = document.getElementById("register");

  addEvent(form, "submit", function(e) {
    var elements = this.elements;
    var username = elements.username.value;
    alert(`Thanks for joining us on our journey ${username}`);
  });
})();
