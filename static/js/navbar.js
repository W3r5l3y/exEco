document.addEventListener('DOMContentLoaded', function() {
    const headerLogoDiv = document.querySelector("#logo-title");
    if (headerLogoDiv) {
        headerLogoDiv.addEventListener("click", function(event) {
            window.location.href = "/dashboard/";
        });
    } else {
        console.log("headerLogoDiv is null");
    }
});