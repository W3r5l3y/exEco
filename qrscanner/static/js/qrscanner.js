document.addEventListener('DOMContentLoaded', function() {
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