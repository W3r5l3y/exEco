document.addEventListener('DOMContentLoaded', () => {
    // Close the error popup
    function closePopup() {
        const popup = document.getElementById('error-popup');
        popup.classList.add('hidden');
        setTimeout(() => popup.style.display = 'none', 300);
    }

    // Add event listener
    const closePopupButton = document.querySelector('.close-btn');
    if (closePopupButton) {
        closePopupButton.addEventListener('click', closePopup);
    }

    // Show error message in popup
    function showError(message) {
        const errorPopup = document.getElementById('error-popup');
        const errorMessage = document.getElementById('error-popup-message');

        errorMessage.textContent = message;
        errorPopup.style.display = 'flex';
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

    // Show the correct tab if present
    if (tab_location) {
        const tab = document.getElementById(tab_location + '-tab-radio');
        tab.click();
    }
});