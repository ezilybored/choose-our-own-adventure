document.addEventListener("DOMContentLoaded", () => {
  const ajax = new XMLHttpRequest();
  ajax.open("GET", "/getoptions");

  ajax.onload = () => {
    const data = JSON.parse(ajax.responseText);

    if (data.success) {
      for (var i = 0; i < data.dates.length; i++) {
        const option = document.createElement("OPTION");
        option.innerHTML = data.dates[i];
        //option.setAttribute("name", "date");
        document.getElementById("datelist").append(option);
      }
    }
  };
  ajax.send();
  return false;
});

/*
(function() {
  const ajax = new XMLHttpRequest();
  ajax.open("GET", "/getoptions");

  ajax.onload = () => {
    const data = JSON.parse(ajax.responseText);

    if (data.success) {
      for (var i = 0; i < data.dates.length; i++) {
        const option = document.createElement("OPTION");
        option.innerHTML = data.dates[i];
        //option.setAttribute("name", "date");
        document.getElementById("datelist").append(option);
      }
    }
  };
  ajax.send();
  return false;
})();
*/
