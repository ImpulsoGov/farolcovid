
function resize_iframe_map() {
    max_width = document.getElementById("chart").getBoundingClientRect()["width"];
    max_height = max_width * 1;
    map = document.getElementsByTagName("svg")[0];
    regions = document.getElementsByClassName("geo borders")[0];
    dimensions_data = regions.getBoundingClientRect();
    //console.log("max_width = ");
    //console.log(max_width)
    //console.log(dimensions_data);
    scale_factor = 1 + Math.min((max_height - dimensions_data["height"]) / dimensions_data["height"], (max_width - dimensions_data["width"]) / dimensions_data["width"]);
    map.setAttribute("transform", "scale(" + scale_factor + ")");
    ymove = -(regions.getBoundingClientRect()["top"] - document.getElementById("chart").getBoundingClientRect()["top"]) - 10;
    xmove = -(regions.getBoundingClientRect()["left"] - document.getElementById("chart").getBoundingClientRect()["left"]);
    //console.log(regions.getBoundingClientRect()["left"]);
    map.setAttribute("transform", "translate(" + xmove + "," + ymove + ") scale(" + (scale_factor - 0.1) + ")");
    //ymove = ymove - (regions.getBoundingClientRect()["top"] + Math.min(document.getElementById("chart").getBoundingClientRect()["top"], document.getElementsByClassName("regions")[0].getBoundingClientRect()["top"])) - 10;
    //map.setAttribute("transform", "translate(" + xmove + "," + ymove + ") scale(" + (scale_factor - 0.2) + ")");
    //console.log(scale_factor);
    //console.log(map);
    //document.getElementById("chart").style.height = regions.getBoundingClientRect()["height"] + "px";
    //document.getElementById("__svelte-dw").style.overflow = "visible";
    //console.log(document.getElementById("chart").style.height);
    //console.log(regions.getBoundingClientRect()["height"] + "px");
    //console.log("data");
    //console.log(xmove);
    //console.log(ymove);
    //console.log(scale_factor);
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