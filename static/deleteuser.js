document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".delete").forEach(button => {
    console.log("socket on");
    button.onclick = () => {
      const ajax = new XMLHttpRequest();
      const userid = button.dataset.userid;
      ajax.open("POST", "/deleteuser", true);

      ajax.onload = () => {
        const data = JSON.parse(ajax.responseText);

        if (data.success) {
          alert(`User deleted`);
          location.reload();
        } else {
          alert(
            `Either you cannot delete this user or they have already been deleted`
          );
        }
      };

      const data = new FormData();
      data.append("id", userid);

      ajax.send(data);
      return false;
    };
  });
});
