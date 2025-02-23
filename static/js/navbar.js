document.addEventListener('DOMContentLoaded', function() {
    const headerLogoDiv = document.querySelector(".header-logo-div");
    if (headerLogoDiv) {
        headerLogoDiv.addEventListener("click", function(event) {
            window.location.href = "/dashboard/";
        });
    }
});