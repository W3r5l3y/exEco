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

    // Select elements
    const dropdown = document.getElementById("transport-unlink-account");
    const unlinkButton = document.getElementById("transport-unlink-button");

    // Fetch linked Strava users and populate dropdown
    fetch("/get-strava-links/")
        .then(response => response.json())
        .then(data => {
            dropdown.innerHTML = ""; 

            if (data.strava_links && data.strava_links.length > 0) {
                data.strava_links.forEach(userId => {
                    const option = document.createElement("option");
                    option.value = userId;
                    option.textContent = `User ID: ${userId}`;
                    dropdown.appendChild(option);
                });
            } else {
                dropdown.innerHTML = '<option value="">No linked accounts found</option>';
            }
        })
        .catch(error => console.error("Error fetching Strava links:", error));

    // Handle Unlink Confirmation
    unlinkButton.addEventListener("click", function () {
        const selectedUserId = dropdown.value;
        if (!selectedUserId) {
            alert("Please select a user to unlink.");
            return;
        }

        fetch(`/unlink-strava/${selectedUserId}/`, {
            method: "POST",
            headers: { "X-CSRFToken": getCSRFToken() } // Needed for Django's CSRF protection
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message); // Show success/error message TODO: Show in HTML clearererer
            location.reload(); // Refresh the dropdown after unlinking
        })
        .catch(error => console.error("Error unlinking Strava:", error));
    });

    // Function to get CSRF token from cookies (needed for POST requests)
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
        return cookieValue || "";
    }

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
