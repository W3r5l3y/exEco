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

    // If a tab is specified, switch to that tab
    if (tab_location) {
        const tabRadio = document.getElementById(`${tab_location}-tab-radio`);
        tabRadio.checked = true;
    }
}