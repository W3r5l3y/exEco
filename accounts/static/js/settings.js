// Close the error popup
function closeErrorPopup() {
    const popup = document.getElementById('error-popup');
    popup.classList.add('hidden');
    setTimeout(() => popup.style.display = 'none', 300);
}

// Close the error popup
function closeSuccessPopup() {
    const popup = document.getElementById('success-popup');
    popup.classList.add('hidden');
    setTimeout(() => popup.style.display = 'none', 300);
}


// Show error message in popup
function showError(message) {
    const errorPopup = document.getElementById('error-popup');
    const errorMessage = document.getElementById('error-popup-message');

    errorMessage.textContent = message;
    errorPopup.style.display = 'flex';
    setTimeout(() => errorPopup.classList.remove('hidden'), 10);
}

function showSuccess(message) {
    const successPopup = document.getElementById('success-popup');
    const successMessage = document.getElementById('success-popup-message');

    successMessage.textContent = message;
    successPopup.style.display = 'flex';

    setTimeout(() => successPopup.classList.remove('hidden'), 10);
}

// Get query parameters from URL
const urlParams = new URLSearchParams(window.location.search);
const error = urlParams.get('error');
const success = urlParams.get('success');

// Show error message if present
if (error) {
    showError(error);
}else if (success){
    showSuccess(success)
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

    if (navbar && content) {
        const navbarHeight = navbar.offsetHeight;
        content.style.paddingTop = navbarHeight + "px";
    }
}

function alterModalUnlink(serviceName){
    document.getElementById("modal-content").className = "";
    document.getElementById("modal-content").classList.add("modal-content");
    document.getElementById("modal-content").classList.add("modal-content-unlink");

    document.getElementById("modal_body_text").innerText = "You can re-link this service at any point";
    document.getElementById("checkModalTitle").innerText = "Un-Link " + serviceName;
    document.getElementById("modalConfirmButton").onclick = function() {
        stravaUnlink();
    };
}

function alterModalDelete(){
    document.getElementById("modal-content").className = "";
    document.getElementById("modal-content").classList.add("modal-content");
    document.getElementById("modal-content").classList.add("modal-content-delete");

    document.getElementById("modal_body_text").innerText = "This action cannot be undone";
    document.getElementById("checkModalTitle").innerText = "DELETE ACCOUNT";
    document.getElementById("modalConfirmButton").onclick = function() {
        confirmDelete();
    };
}

function confirmDelete() {
    document.getElementById("delete_form").submit();
}
function logOut() {
    document.getElementById("log_out_form").submit();
}

function stravaUnlink(){
    document.getElementById("strava_form").submit();
}