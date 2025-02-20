// Close the error popup
function closePopup() {
    const popup = document.getElementById('error-popup');
    popup.classList.add('hidden');
    setTimeout(() => popup.style.display = 'none', 300);
}

// Show error message in popup
function showError(message) {
    const errorPopup = document.getElementById('error-popup');
    const errorMessage = document.getElementById('error-popup-message');

    errorMessage.textContent = message;
    errorPopup.style.display = 'flex'; // Make it visible
    setTimeout(() => errorPopup.classList.remove('hidden'), 10);
}

// Get query parameters from URL
const urlParams = new URLSearchParams(window.location.search);
const error = urlParams.get('error');
const tab_location = urlParams.get('tab');

// Show error message if present
if (error) {
    showError(error);
}


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