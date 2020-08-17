
function init_listener() {
    //state map
    document.getElementsByTagName("svg")[0].addEventListener("click", function () {
        window.parent.document.getElementsByClassName("st-bu st-bv st-ae st-b8 st-ak st-dc st-dd")[2].click();
        state_map_choice = document.getElementsByClassName("dw-tooltip")[0].getElementsByTagName("h2")[0];
        result = state_map_choice.textContent;
        //document.getElementsByClassName("dw-tooltip")[0].style["display"] = 'none';
        options = window.parent.document.getElementsByClassName("st-ai st-bo");
        for (i = 0; i < options.length; i++) {
            if (options[i].textContent == result) {
                options[i].click();
                document.getElementsByTagName("svg")[0].focus();
                break;
            }
        }
    });
}
