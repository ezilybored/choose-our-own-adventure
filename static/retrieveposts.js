document.addEventListener("DOMContentLoaded", () => {
  document.querySelector("#enterdate").onchange = () => {
    const ajax = new XMLHttpRequest();
    const date = document.querySelector("#datelist").value;
    ajax.open("POST", "/retrieveposts");

    ajax.onload = () => {
      const data = JSON.parse(ajax.responseText);

      if (data.success) {
        const post = `${data.post}`;
        const postid = `${data.postid}`;
        document.getElementById("postedit").innerHTML = post;
        document.getElementById("postid").innerHTML = postid;
      } else {
        document.getElementById(
          "postedit"
        ).innerHTML = `Unfortunately there were no story posts on that date`;
      }
    };

    const data = new FormData();
    data.append("date", date);

    ajax.send(data);
    return false;
  };
});
