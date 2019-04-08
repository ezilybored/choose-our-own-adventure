document.addEventListener("DOMContentLoaded", () => {
  var socket = io.connect(
    location.protocol + "//" + document.domain + ":" + location.port
  );

  socket.on("connect", () => {
    document.querySelectorAll("button").forEach(button => {
      button.onclick = () => {
        const selection = button.dataset.vote;
        socket.emit("submit vote", { selection: selection });
      };
    });
  });

  socket.on("vote totals", data => {
    document.querySelector("#A").innerHTML = data.A;
    document.querySelector("#B").innerHTML = data.B;
    document.querySelector("#C").innerHTML = data.C;
    document.querySelector("#D").innerHTML = data.D;
  });

  socket.on("vote json", data => {
    var votedata = data;

    // Clears the old data
    d3.select("svg").remove();

    var margin = { left: 90, top: 16, right: 30, bottom: 85 };
    var barchart_width = 800 - margin.left - margin.right;
    var barchart_height = 400 - margin.top;
    var bar_padding = 5;

    // These hex are the codes for the bootstrap colors
    var color = d3.scaleOrdinal(["#0275d8", "#d9534f", "#5cb85c", "#f0ad4e"]);

    var svg = d3
      .select("#barchart")
      .append("svg")
      .attr("width", barchart_width)
      .attr("height", barchart_height);

    // Binds the data and creates the bars
    svg
      .selectAll("rect")
      .data(votedata)
      .enter()
      .append("rect")
      // Sets the distance between the bars. parametsr are d = data, i = index
      .attr("x", function(d, i) {
        return i * (barchart_width / votedata.length);
      })
      .attr("y", function(d) {
        return barchart_height - d * 5;
      })
      .attr("width", barchart_width / votedata.length - bar_padding)
      .attr("height", function(d) {
        return d * 5;
      })
      .attr("fill", function(d, i) {
        return color(i);
      });

    // Adding labels to the graph
    svg
      .selectAll("text")
      .data(votedata)
      .enter()
      .append("text")
      .text(function(d) {
        return d;
      })
      // Centralises the text to the middle of the bar
      .attr("x", function(d, i) {
        return (
          i * (barchart_width / votedata.length) +
          (barchart_width / votedata.length - bar_padding) / 2
        );
      })
      .attr("y", function(d) {
        return barchart_height - d * 2 - 15;
      })
      .attr("font-size", 22)
      .attr("fill", "purple")
      .attr("text-anchor", "middle");
  });
});
