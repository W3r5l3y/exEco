document.addEventListener('DOMContentLoaded', function() {
    // Add event listener to the logo div to redirect to the dashboard
    const headerLogoDiv = document.querySelector("#logo-title");
    if (headerLogoDiv) {
        headerLogoDiv.addEventListener("click", function(event) {
            window.location.href = "/dashboard/";
        });
    } else {
        console.log("headerLogoDiv is null");
    }
});