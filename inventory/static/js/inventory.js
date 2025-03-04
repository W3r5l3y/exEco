document.addEventListener("DOMContentLoaded", function () {
    // Function to open a lootbox
    function openLootbox(lootboxId, button) {
        fetch(`/open-lootbox/${lootboxId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/json"
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayLootboxResult(data.item_won, button, data.lootbox_removed);
                } else {
                    alert(data.error || "Something went wrong!");
                }
            })
            .catch(error => console.error("Error:", error));
    }

    // Function to display the lootbox result with animation sequence
    function displayLootboxResult(item, button, lootboxRemoved) {
        // Get popup elements
        const popupOverlay = document.getElementById("popup-overlay");
        const lootboxImageContainer = document.getElementById("lootbox-image-container");
        const resultContainer = document.getElementById("lootbox-item-result");
        const popupTitle = document.getElementById("popup-title");
        const popupImage = document.getElementById("popup-image");
        const popupDescription = document.getElementById("popup-description");
        const closeBtn = document.getElementById("popup-close");

        // Add event listener to close button
        closeBtn.addEventListener("click", function () {
            popupOverlay.style.display = "none";
            updateInventory();
        });
    
        // Clear the popup elements
        lootboxImageContainer.innerHTML = "";
        resultContainer.style.display = "none";
        closeBtn.style.display = "none";
        lootboxImageContainer.style.display = "flex";
    
        // Show the popup overlay
        popupOverlay.style.display = "flex";
    
        // Get the static image source and replace it with the video source
        const staticSrc = button.getAttribute("data-static-src");
        const videoSrc = staticSrc.replace(".png", "_animation.mp4");
    
        // Create video element
        const video = document.createElement("video");
        video.src = videoSrc;
        video.controls = false;
        video.classList.add("lootbox-media");
        video.playbackRate = 0.75;
    
        // Pause the video when it's loaded
        video.pause();
    
        lootboxImageContainer.appendChild(video);
    
        // Play video when clicked
        video.addEventListener("click", function playVideo() {
            video.removeEventListener("click", playVideo);
            video.play();
        });
    
        // When the video finishes...
        video.addEventListener("ended", function() {
            // Capture the final frame's color using a canvas
            const canvas = document.createElement("canvas");
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext("2d");
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            // Sample the center pixel's color
            const x = Math.floor(canvas.width / 2);
            const y = Math.floor(canvas.height / 2);
            const pixel = ctx.getImageData(x, y, 1, 1).data;
            const rgb = `rgb(${pixel[0]}, ${pixel[1]}, ${pixel[2]})`;
            // Set a CSS variable with that color
            document.documentElement.style.setProperty('--lootbox-animation-final-colour', rgb);
    
            // Remove the video element and show the result
            video.remove();
            lootboxImageContainer.style.display = "none";
    
            // Show the lootbox result
            popupTitle.innerText = `${item.name}`;
            if (item.image) {
                popupImage.src = item.image;
                popupImage.alt = item.name;
                popupImage.style.display = "flex";
            } else {
                popupImage.style.display = "none";
            }
            popupDescription.innerText = item.description || "";
            resultContainer.style.display = "flex";
            closeBtn.style.display = "flex";
        });
    }    

    // Function to update the inventory
    function updateInventory() {
        fetch("/get-inventory/")
            .then(response => response.text())
            .then(html => {
                document.querySelector("#inventory-container").innerHTML = html;
                lootboxEventListeners();
                regularItemEventListeners();
            })
            .catch(error => console.error("Error updating inventory:", error));
    }

    // Function to attach event listeners to lootbox buttons
    function lootboxEventListeners() {
        document.querySelectorAll(".lootbox-btn").forEach(button => {
            button.addEventListener("click", function () {
                const lootboxId = this.getAttribute("data-item-id");
                openLootbox(lootboxId, this);
            });
        });
    }

    // Function to attach event listeners to regular item buttons
    function regularItemEventListeners() {
        document.querySelectorAll(".item-btn").forEach(button => {
            button.addEventListener("click", function () {
                window.location.href = `/garden/`;
            });
        });
    }

    // Function to get the CSRF token
    function getCSRFToken() {
        const cookies = document.cookie.split("; ");
        for (let cookie of cookies) {
            if (cookie.startsWith("csrftoken=")) {
                return cookie.split("=")[1];
            }
        }
        return "";
    }

    // Attach initial event listeners
    lootboxEventListeners();
    regularItemEventListeners();
});
