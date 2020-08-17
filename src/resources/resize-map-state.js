
function resize_iframe_map() {
    max_width = document.getElementById("chart").getBoundingClientRect()["width"];
    max_height = max_width * 1;
    map = document.getElementsByTagName("svg")[0];
    regions = document.getElementsByClassName("geo borders")[0];
    dimensions_data = regions.getBoundingClientRect();
    console.log("max_width = ");
    console.log(max_width)
    console.log(dimensions_data);
    scale_factor = 1 + Math.min((max_height - dimensions_data["height"]) / dimensions_data["height"], (max_width - dimensions_data["width"]) / dimensions_data["width"]);
    ymove = -(dimensions_data["top"] - document.getElementById("chart").getBoundingClientRect()["top"]);
    xmove = (dimensions_data["left"] - document.getElementById("chart").getBoundingClientRect()["left"]);
    map.setAttribute("transform", "translate(" + xmove + "," + ymove + ") scale(" + scale_factor + ")");
    console.log(scale_factor);
    console.log(map);
    console.log(regions);
    console.log(regions.getBoundingClientRect());
    console.log(document.getElementById("chart"));
    console.log(document.getElementById("chart").getBoundingClientRect());
}