document.addEventListener("DOMContentLoaded", () => {
    // Get the garden wrapper element and add the grid items
    const gardenWrapper = document.querySelector(".garden-wrapper");
    for (let row = 1; row <= 9; row++) {
        for (let col = 1; col <= 9; col++) {
            const cell = document.createElement("div");
            cell.classList.add("grid-item", `grid-item-${row}-${col}`);
            cell.textContent = `${row},${col}`; // For debugging

            gardenWrapper.appendChild(cell);
        }
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
});