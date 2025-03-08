document.addEventListener("DOMContentLoaded", function () {
    /* --------------------------------------------------
        QR Scanner
    -------------------------------------------------- */

    // Add qr code to database
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
            
            // API endpoint
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

    // Add qr points to user
    const qrScannerPointsForm = document.getElementById("qrscanner-points-form");
    if (qrScannerPointsForm) {
        qrScannerPointsForm.addEventListener("submit", function (event) {
            event.preventDefault(); // Prevent form from reloading the page

            // Get input values
            const userId = document.getElementById("qrscanner-points-user-id").value;
            const amount = document.getElementById("qrscanner-points-amount").value;
            
            // API endpoint
            const apiUrl = `/add-points/qr/${userId}/${amount}/`;

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
                resultContainer.id = "qr-points-result";
                
                alert(`${amount} qr points added to user ${userId}.`);
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred while adding points.");
            });
        });
    }

    /* --------------------------------------------------
        Bingame
    -------------------------------------------------- */

    // Add bingame points to user
    const bingamePointsForm = document.getElementById("bingame-points-form");
    if (bingamePointsForm) {
        bingamePointsForm.addEventListener("submit", function (event) {
            event.preventDefault(); // Prevent form from reloading the page

            // Get input values
            const userId = document.getElementById("bingame-points-user-id").value;
            const amount = document.getElementById("bingame-points-amount").value;
            
            // API endpoint
            const apiUrl = `/add-points/bingame/${userId}/${amount}/`;

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
                resultContainer.id = "bingame-points-result";
                
                alert(`${amount} bingame points added to user ${userId}.`);
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred while adding points.");
            });
        });
    }

    /* --------------------------------------------------
        Transport
    -------------------------------------------------- */

    // Add transport points to user
    const transportPointsForm = document.getElementById("transport-points-form");
    if (transportPointsForm) {
        transportPointsForm.addEventListener("submit", function (event) {
            event.preventDefault(); // Prevent form from reloading the page

            // Get input values
            const userId = document.getElementById("transport-points-user-id").value;
            const amount = document.getElementById("transport-points-amount").value;
            
            // API endpoint
            const apiUrl = `/add-points/transport/${userId}/${amount}/`;

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
                resultContainer.id = "transport-points-result";
                
                alert(`${amount} transport points added to user ${userId}.`);
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred while adding points.");
            });
        });
    }

    /* --------------------------------------------------
        Forum
    -------------------------------------------------- */

});
