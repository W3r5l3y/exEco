
function profileReset(){
    const email_input = document.getElementById('email');
    const first_name_input = document.getElementById('first_name');
    const last_name_input = document.getElementById('last_name');

    email_input.value = email_input.dataset.email;
    first_name_input.value = first_name_input.dataset.firstname;
    last_name_input.value = last_name_input.dataset.lastname;
}


window.onload = function () {
    adjustNavBarHeight();
}

function adjustNavBarHeight(){
    const navbar = document.getElementById("navbar");
    const content = document.getElementById("settings");
    console.log(navbar)
    console.log(content)
    if (navbar && content) {
        console.log("yo")
        const navbarHeight = navbar.offsetHeight;
        content.style.paddingTop = navbarHeight + "px";
    }
}