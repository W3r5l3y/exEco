document.addEventListener("DOMContentLoaded", function () {
    // Function to get CSRF token from cookies (needed for POST requests)
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
        return cookieValue || "";
    }

    /* --------------------------------------------------
    Drop down menu logic, for adding points to bingame, transport and qr scanner.
    -------------------------------------------------- */
    function fetchUserIds() {
        fetch("/get-user-ids/")
            .then(response => response.json())
            .then(data => {
                if (data.user_ids && data.user_ids.length > 0) {
                    console.log("User IDs found:", data.user_ids);
                    updateDropdowns(data.user_ids);
                } else {
                    console.error("No user IDs found.");
                }
            })
            .catch(error => console.error("Error fetching user IDs:", error));
    }

    function updateDropdowns(users) {
        const dropdowns = [
            document.getElementById("qrscanner-points-user-id"),
            document.getElementById("bingame-points-user-id"),
            document.getElementById("transport-points-user-id"),
        ];

        dropdowns.forEach(dropdown => {
            if (dropdown) {
                dropdown.innerHTML = "";
                const defaultOption = document.createElement("option");
                defaultOption.disabled = true;
                defaultOption.selected = true;
                defaultOption.value = "";
                defaultOption.textContent = "Select a user";
                dropdown.appendChild(defaultOption);

                users.forEach(user => {
                    const option = document.createElement("option");
                    option.value = user.id;
                    option.textContent = `${user.email || "Unknown"} (ID: ${user.id})`;
                    dropdown.appendChild(option);
                });
            }
        });
    }

    fetchUserIds();

    /* --------------------------------------------------
        QR Scanner
    -------------------------------------------------- */

    /* ----------
        Add QR location to database
    ---------- */
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
                    refreshQrSelect(); // Refresh dropdown after adding new QR code
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

    /* ----------
        Review QR code entries and allow disabling
    ---------- */
    const qrScannerQrSelect = document.getElementById("qrscanner-qr-select");
    const qrScannerQrEnable = document.getElementById("qrscanner-qr-enable");
    const qrScannerQrDisable = document.getElementById("qrscanner-qr-disable");

    function refreshQrSelect() {
        fetch("/get-qr-codes/")
        .then(response => response.json())
        .then(data => {
            qrScannerQrSelect.innerHTML = ""; // Clear dropdown

            // Add a disabled option with 'Select a QR code' text
            const defaultOption = document.createElement("option");
            defaultOption.disabled = true;
            defaultOption.selected = true;
            defaultOption.value = "";
            defaultOption.textContent = "Select a QR code";
            qrScannerQrSelect.appendChild(defaultOption);
            
            if (data.qr_codes && data.qr_codes.length > 0) {
                data.qr_codes.forEach(qrCode => {
                    const option = document.createElement("option");
                    option.value = qrCode.id;
                    option.textContent = qrCode.location_name + (qrCode.is_active ? " (Active)" : " (Disabled)");
                    qrScannerQrSelect.appendChild(option);
                });
            } else {
                qrScannerQrSelect.innerHTML = '<option value="">No QR codes found</option>';
            }
        })
        .catch(error => console.error("Error fetching QR codes:", error));
    }

    refreshQrSelect();

    qrScannerQrEnable.addEventListener("click", function () {
        const selectedQrId = qrScannerQrSelect.value;
        if (!selectedQrId) {
            alert("Please select a QR code to enable.");
            return;
        }
        
        fetch(`/enable-qr/${selectedQrId}/`, {
            method: "POST",
            headers: { "X-CSRFToken": getCSRFToken() }
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            location.reload();
        })
        .catch(error => console.error("Error enabling QR code:", error));
    });

    qrScannerQrDisable.addEventListener("click", function () {
        const selectedQrId = qrScannerQrSelect.value;
        if (!selectedQrId) {
            alert("Please select a QR code to disable.");
            return;
        }
        
        fetch(`/disable-qr/${selectedQrId}/`, {
            method: "POST",
            headers: { "X-CSRFToken": getCSRFToken() }
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            location.reload();
        })
        .catch(error => console.error("Error disabling QR code:", error));
    });

    /* ----------
        Add qr points to user
    ---------- */
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

    // <div class="gamekeeper-section-task gamekeeper-sub-section">
    //             <h3>Add bin game entries into the database</h3>
    //             <form id="bingame-form">
    //                 <label for="bingame-item-picture">Item Picture</label>
    //                 <input type="file" id="bingame-item-picture" name="item_picture" required>
    //                 <label for="bingame-item-name">Item Name</label>
    //                 <input type="text" id="bingame-item-name" placeholder="Item name" name="item_name" required>
    //                 <label for="bingame-item-bin-id">Bin Id</label>
    //                 <input type="text" id="bingame-item-bin-id" placeholder="Bin id" name="item_bin_id" required>
    //                 <button type="bingame-add-button">Submit</button>
    //             </form>
    //         </div>

    /* ----------
        Add bingame item to database
    ---------- */
    const bingameForm = document.getElementById("bingame-form");
    if (bingameForm) {
        bingameForm.addEventListener("submit", function (event) {
            // Clear previous result
            const previousResult = document.getElementById("bingame-result");
            if (previousResult) {
                previousResult.remove();
            }
            
            event.preventDefault(); // Prevent form from reloading the page

            // Get input values
            const itemPicture = document.getElementById("bingame-item-picture").files[0];
            const itemName = document.getElementById("bingame-item-name").value;
            const itemBinId = document.getElementById("bingame-item-bin-id").value;

            // Create FormData object to send file and text data
            const formData = new FormData();
            formData.append("item_picture", itemPicture);
            formData.append("item_name", itemName);
            formData.append("item_bin_id", itemBinId);

            // API endpoint
            const apiUrl = "/add-item-to-bingame/";

            // Send request to Django view
            fetch(apiUrl, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCSRFToken(),
                },
            })
            .then(response => response.json())
            .then(data => {
                const resultContainer = document.createElement("div");
                resultContainer.id = "bingame-result";
            
                if (data.item_id) {
                    resultContainer.innerHTML = `<p>Item added successfully with ID: ${data.item_id}</p>`;
                } else if (data.error) {
                    resultContainer.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
                }
            
                // Append result below form
                bingameForm.appendChild(resultContainer);
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred while adding the item.");
            });
        });
    }

    /* ----------
        Add bingame points to user
    ---------- */
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

    /* ----------
        Get linked Strava users and allow unlinking
    ---------- */
    const dropdown = document.getElementById("transport-unlink-account");
    const unlinkButton = document.getElementById("transport-unlink-button");

    // Fetch linked Strava users and populate dropdown
    fetch("/get-strava-links/")
        .then(response => response.json())
        .then(data => {
            dropdown.innerHTML = "";

            // Add a disabled option with 'Select a user' text
            const defaultOption = document.createElement("option");
            defaultOption.disabled = true;
            defaultOption.selected = true;
            defaultOption.value = "";
            defaultOption.textContent = "Select a user";
            dropdown.appendChild(defaultOption);

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

    /* ----------
        Add transport points to user
    ---------- */
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

    /* --------------------------------------------------
        Shop
    -------------------------------------------------- */
    const shopForm = document.getElementById("shop-form");
    if (shopForm) {
        shopForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const itemPicture = document.getElementById("shop-item-picture").files[0];
            const itemName = document.getElementById("shop-item-name").value;
            const itemPrice = document.getElementById("shop-item-price").value;
            const itemDescription = document.getElementById("shop-item-description").value;

            if (!itemPicture || !itemName || !itemPrice || !itemDescription) {
                alert("Please fill in all fields.");
                return;
            }

            const formData = new FormData();
            const item_picture = new File([itemPicture], itemPicture.name.replace(/ /g, "_"), { type: itemPicture.type });
            //item_picture.name = itemPicture.name.replace(/ /g, "_")
            formData.append("item_picture", item_picture);
            formData.append("item_name", itemName);
            formData.append("item_price", itemPrice);
            formData.append("item_description", itemDescription);

            fetch("/add-item-to-shop/", {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.item_id) {
                    alert(`Item added successfully with ID: ${data.item_id}`);
                } else if (data.error) {
                    alert(`Error: ${data.error}`);
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("An error occurred while adding the item.");
            });
        });
    }

    /* --------------------------------------------------
        Challenges
    -------------------------------------------------- */
    const challengesForm = document.getElementById('challenges-form');
    if (challengesForm) {
        challengesForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(challengesForm);
            
            fetch('/add-challenge/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCSRFToken(),
                },
            })
            .then(response => {
                if (response.ok) {
                    alert("Challenge added successfully!");
                challengesForm.reset();
                } else {
                    alert("Error adding challenge.");
                }
            })
            .catch(error => {
                console.error(error);
                alert("Error adding challenge.");
            });
        });
    }
});