document.addEventListener("DOMContentLoaded", function() {
    /* --------------------------------------------------
        Leaflet Map Code & Popup Logic
    -------------------------------------------------- */
    var map;

    // Function to initialize the Leaflet map with location pins
    function initializeLeafletMap() {
        if (!map) {
            map = L.map("map").setView([50.73555553269732, -3.5337938165488967], 16);
            
            // Add an OpenStreetMap tile layer
            L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
                attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
            }).addTo(map);
            
            
            var customIcon = L.icon({
                iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png",
                shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
                iconSize: [25, 41], // Default Leaflet marker size
                iconAnchor: [12, 41], // Positioning
                popupAnchor: [1, -34]
            });
            
            
            
            // Fetch location pins from the Django view
            fetch('/locations-json/')
                .then(response => response.json())
                .then(locations => {
                    locations.forEach(loc => {
                        // Check that latitude and longitude are valid
                        if (loc.latitude && loc.longitude) {
                            L.marker([loc.latitude, loc.longitude], { icon: customIcon })
                                .addTo(map)
                                .bindPopup(`${loc.location_name}`);
                        }
                    });
                })
                .catch(error => console.error("Error fetching locations:", error));
        }
    }
    
    
    // Set popup listener objects
    var openMapPopupButton = document.getElementById("open-map-popup-button");
    var mapPopupContainer = document.getElementById("map-popup");
    var closeMapPopupButton = document.getElementById("close-map-popup");
    
    // Open the map popup
    if (openMapPopupButton) {
        openMapPopupButton.addEventListener("click", function() {
            mapPopupContainer.style.display = "block";
            initializeLeafletMap();
            setTimeout(function() {
                map.invalidateSize();
            }, 200);
        });
    }
    
    // Close the map popup
    if (closeMapPopupButton) {
        closeMapPopupButton.addEventListener("click", function() {
            mapPopupContainer.style.display = "none";
        });
    }    

    // QR Scanner Popup Logic
    var closeQrBtn = document.getElementById("close-qr-popup");
    if (closeQrBtn) {
        closeQrBtn.addEventListener("click", function() {
            var qrPopup = document.getElementById("qr-popup");
            if (qrPopup) {
                qrPopup.style.display = "none";
            }
        });
    }

    /* --------------------------------------------------
        Lootbox Logic
    -------------------------------------------------- */
    
    // Check if lootboxes were awarded from the HTML template
    const lootboxCountElem = document.getElementById("lootbox-count");
    if (lootboxCountElem) {
        const lootboxesFromHTML = parseInt(lootboxCountElem.value, 10) || 0;
        console.log("Lootboxes awarded from HTML,", lootboxesFromHTML);
        if (lootboxesFromHTML > 0) {
            showLootboxesAwarded(2, lootboxesFromHTML);
        }
    }

    // Function to display lootbox popup
    function showLootboxesAwarded(lootbox_id, quantity) {
        // Create popup elements
        const lootboxPopup = document.createElement("div");
        lootboxPopup.id = "lootbox-popup";

        const lootboxContent = document.createElement("div");
        lootboxContent.id = "lootbox-content";
        lootboxPopup.appendChild(lootboxContent);

        // Fetch lootbox data from the server
        fetch(`/get-lootbox-data/?lootbox_id=${lootbox_id}`)
            .then(response => response.json())
            .then(data => {
                const lootboxImage = document.createElement("img");
                lootboxImage.src = data.lootbox_image;
                lootboxImage.alt = data.lootbox_name;
                lootboxContent.appendChild(lootboxImage);

                const lootboxName = document.createElement("p");
                lootboxName.textContent = data.lootbox_name;
                lootboxContent.appendChild(lootboxName);

                const lootboxQuantity = document.createElement("p");
                lootboxQuantity.textContent = `Quantity: ${quantity}`;
                lootboxContent.appendChild(lootboxQuantity);

                const lootboxCloseBtn = document.createElement("button");
                lootboxCloseBtn.textContent = "Close";
                lootboxCloseBtn.addEventListener("click", () => {
                    lootboxPopup.remove();
                });
                lootboxContent.appendChild(lootboxCloseBtn);

                document.body.appendChild(lootboxPopup);
            })
            .catch(error => console.error("Error fetching lootbox data:", error));
    }

    // Handle qr scanner form submission
    const fileInput = document.querySelector("input[name='image']");
    if (fileInput) {
        fileInput.addEventListener("change", function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.getElementById("qr-preview");
                    if (img) {
                        img.src = e.target.result;
                        img.style.display = "block";
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Function to update the leaderboard
    function updateLeaderboard() {
        fetch("/get-qrscanner-leaderboard/")
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error("Error fetching leaderboard:", data.error);
                    return;
                }
                // Sort leaderboard data by points in descending order
                data.sort((a, b) => b.points - a.points);
                for (let i = 0; i < 10; i++) {
                    const leaderboardItem = document.getElementById(`leaderboard-item-${i + 1}`);
                    if (leaderboardItem) {
                        if (data[i]) {
                            leaderboardItem.textContent = `${data[i].username} - ${data[i].qrscanner_points} pts`;
                        } else {
                            leaderboardItem.textContent = "---"; // Placeholder if no data
                        }
                    }
                }
            })
            .catch(error => console.error("Error fetching leaderboard:", error));
    }

    updateLeaderboard();
});