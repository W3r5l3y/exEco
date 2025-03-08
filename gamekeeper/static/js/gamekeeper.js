document.addEventListener("DOMContentLoaded", function () {
    /* --------------------------------------------------
        QR Scanner
    -------------------------------------------------- */
    const qrScannerForm = document.getElementById("qrscanner-form");

    if (qrScannerForm) {
        qrScannerForm.addEventListener("submit", function (event) {
            event.preventDefault(); // Prevent form from reloading the page

            // Get input values
            const locationCode = document.getElementById("qrscanner-location-code").value;
            const locationName = document.getElementById("qrscanner-location-name").value;
            const locationFact = document.getElementById("qrscanner-location-fact").value;
            const cooldownLength = document.getElementById("qrscanner-location-cooldown").value || 60; // Default 60s
            const locationValue = document.getElementById("qrscanner-location-value").value || 1; // Default 1
            
            // API endpoint (adjust URL if necessary)
            const apiUrl = `/add-location-to-qr/${encodeURIComponent(locationCode)}/${encodeURIComponent(locationName)}/${encodeURIComponent(locationFact)}/${cooldownLength}/${locationValue}/`;

            // Send request to Django view
            fetch(apiUrl, {
                method: "GET",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
            .then(response => response.json())
            .then(data => {
                const resultContainer = document.createElement("div");
                resultContainer.id = "qr-result";
                
                if (data.qr_code_url) {
                    resultContainer.innerHTML = `
                        <p>QR Code Generated Successfully:</p>
                        <img src="${data.qr_code_url}" alt="QR Code for ${locationCode}" width="200">
                    `;
                } else if (data.error) {
                    resultContainer.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
                }

                // Append result below form
                qrScannerForm.appendChild(resultContainer);
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred while generating the QR code.");
            });
        });
    }


    /* --------------------------------------------------
        Bingame
    -------------------------------------------------- */


    /* --------------------------------------------------
        Transport
    -------------------------------------------------- */


    /* --------------------------------------------------
        Forum
    -------------------------------------------------- */
});
