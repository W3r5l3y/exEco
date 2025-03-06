//lootboxesFromHTML = 0;
document.addEventListener('DOMContentLoaded', function() {
    // Get lootboxes count from the hidden input in HTML
    const lootboxCountElem = document.getElementById("lootbox-count"); // CHANGED
    if (lootboxCountElem) { // CHANGED
        const lootboxesFromHTML = parseInt(lootboxCountElem.value, 10) || 0; // CHANGED
        console.log("Lootboxes awarded from HTML,", lootboxesFromHTML);
        
        if (lootboxesFromHTML > 0) { // CHANGED
            showLootboxesAwarded(lootboxesFromHTML); // CHANGED
            // Reset lootbox count value after showing the alert
            //lootboxesFromHtml = 0; // CHANGED - Prevents multiple popups
        };
    };
    
    // Display the QR code scanner image preview
    const fileInput = document.querySelector("input[name='image']");
    if (fileInput) {
        fileInput.addEventListener("change", function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const img = document.getElementById("qr-preview");
                    img.src = e.target.result;
                    img.style.display = "block";
                };
                reader.readAsDataURL(file);
            }
        });
    updateLeaderboard();
    }

    function showLootboxesAwarded(lootboxesAwarded) {
        alert(`You earned ${lootboxesAwarded} lootboxes!`);
    }

    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }

    // Function to update leaderboard on page
    function updateLeaderboard() {
        fetch("/get-qrscanner-leaderboard/")
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error("Error fetching leaderboard:", data.error);
                    return;
                }
    
                // Sort by points in descending order
                data.sort((a, b) => b.points - a.points);
    
                // Loop through the leaderboard items and update them
                for (let i = 0; i < 10; i++) {
                    const leaderboardItem = document.getElementById(`leaderboard-item-${i + 1}`);
    
                    if (leaderboardItem) {
                        if (data[i]) {
                            leaderboardItem.textContent = `${data[i].username} - ${data[i].qrscanner_points} pts`;
                        } else {
                            leaderboardItem.textContent = "---";  // Placeholder if no data
                        }
                    }
                }
            })
            .catch(error => console.error("Error fetching leaderboard:", error));
    }

    updateLeaderboard();
});