
function resize_iframe_map() {
    max_width = document.getElementById("chart").getBoundingClientRect()["width"];
    max_height = max_width * 0.9;
    map = document.getElementsByTagName("svg")[0];
    regions = document.getElementsByClassName("geo borders")[0];
    dimensions_data = regions.getBoundingClientRect();
    //console.log("max_width = ");
    //console.log(max_width)
    //console.log(dimensions_data);
    scale_factor = 1 + 0.8 * Math.min((max_height - dimensions_data["height"]) / dimensions_data["height"], (max_width - dimensions_data["width"]) / dimensions_data["width"]);
    map.setAttribute("transform", "scale(" + scale_factor + ")");
    ymove = -(regions.getBoundingClientRect()["top"] - document.getElementById("chart").getBoundingClientRect()["top"]);
    xmove = -(regions.getBoundingClientRect()["left"] - document.getElementById("chart").getBoundingClientRect()["left"]);
    //console.log(regions.getBoundingClientRect()["left"]);
    map.setAttribute("transform", "translate(" + xmove + "," + ymove + ") scale(" + scale_factor + ")");
    //console.log(scale_factor);
    //console.log(map);
    //console.log(xmove);
    //console.log(regions);
    //console.log(regions.getBoundingClientRect());
    //console.log(document.getElementById("chart"));
    //console.log(document.getElementById("chart").getBoundingClientRect());
    //console.log(regions.getBoundingClientRect()["left"]);
    //console.log(map.getBoundingClientRect());
    window.frameElement.style.height = map.getBoundingClientRect()["height"] + "px";
}

function addResizeListener() {
    window.parent.addEventListener('resize', resize_iframe_map);
}