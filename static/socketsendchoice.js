document.addEventListener("DOMContentLoaded", () => {
  var socket = io.connect(
    location.protocol + "//" + document.domain + ":" + location.port
  );

  socket.on("connect", () => {
    document.querySelectorAll(".selecta").forEach(button => {
      console.log("socket on");
      button.onclick = () => {
        const ajax = new XMLHttpRequest();
        ajax.open("POST", "/votecheck", true);

        ajax.onload = function() {
          const data = JSON.parse(ajax.responseText);
          if (data.success == true) {
            const selection = button.dataset.vote;
            console.log(selection);
            const postid = `${data.postid}`;
            alert(
              `Thanks for choosing. This week you chose option: ${selection}`
            );
            socket.emit("submit vote", {
              selection: selection,
              postid: postid
            });
          } else if (data.success == "Not") {
            alert(
              `Voting for this week has closed. Try again after the next installment on Sunday`
            );
          } else {
            alert(
              `You have already chosen this week. Try again after the next installment on Sunday`
            );
          }
        };
        ajax.send();
        return false;
      };
    });
  });
});
