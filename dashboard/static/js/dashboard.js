document.addEventListener("DOMContentLoaded", () => {
    const gardenWrapper = document.getElementById("garden-wrapper");
    // Put user's garden image in garden wrapper [.../garden/static/gardens/garden_state_user<x>.png]
    
    // Function to get user's garden state image
    function getUserGardenImage() {
        fetch("/fetch-user-garden-image/")
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error("Error fetching user garden image:", data.error);
                    return;
                }

                // Append user's garden image to garden wrapper child element
                const gardenImage = document.createElement("img");
                gardenImage.src = data.image_url;
                gardenImage.alt = "Garden state";
                gardenWrapper.appendChild(gardenImage);
            })
            .catch(error => console.error("Error fetching user garden image:", error));
    }

    // Function to update leaderboard on page
    function updateLeaderboard() {
        fetch("/get-total-leaderboard/")
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error("Error fetching leaderboard:", data.error);
                    return;
                }
    
                // Sort by points in descending order
                data.sort((a, b) => b.points - a.points);
    
                // Loop through the leaderboard items and update them
                for (let i = 0; i < 5; i++) { // Only show top 5
                    const leaderboardItem = document.getElementById(`leaderboard-item-${i + 1}`);
    
                    if (leaderboardItem) {
                        if (data[i]) {
                            leaderboardItem.textContent = `${data[i].username} - ${data[i].total_points} pts`;
                        } else {
                            leaderboardItem.textContent = "---";  // Placeholder if no data
                        }
                    }
                }
            })
            .catch(error => console.error("Error fetching leaderboard:", error));
    }

    updateLeaderboard();

    getUserGardenImage();

    // Add event listener to garden wrapper to redirect to garden page
    gardenWrapper.addEventListener("click", () => {
        window.location.href = "/garden/";
    });
});