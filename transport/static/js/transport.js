document.addEventListener("DOMContentLoaded", function() {
    const logBtn = document.getElementById("log-btn");
    if (logBtn) {
        document.getElementById("log-btn").addEventListener("click", function() {
            document.getElementById("log-popup").style.display = "flex";

            // Fetch last 5 activities from Strava
            fetch("/get-last-five-activities/")
                .then(response => response.json())
                .then(data => {
                    const select = document.getElementById("activity-select");
                    select.innerHTML = '<option value="" disabled selected>Select an activity</option>'; // Reset options
                    
                    if (data.error) {
                        console.error("Error fetching activities:", data.error);
                        return;
                    }

                    data.forEach(activity => {
                        const option = document.createElement("option");
                        option.value = activity.id;
                        option.textContent = `${activity.name} - ${(activity.distance / 1000).toFixed(2)} km`;
                        option.dataset.distance = activity.distance; // Store distance
                        option.dataset.type = activity.type; // Store type (walk, run, cycle)
                        select.appendChild(option);
                    });
                })
                .catch(error => console.error("Error fetching activities:", error));
        });
    }

    document.getElementById("submit-activity").addEventListener("click", function() {
        const selectedActivity = document.getElementById("activity-select").value; // Strava activity ID
        const selectedType = document.getElementById("activity-select").selectedOptions[0].dataset.type; // walk, run, cycle
        const selectedDistance = Number(document.getElementById("activity-select").selectedOptions[0].dataset.distance); // Distance in meters
        const selectedOption = document.querySelector('input[name="activity-option"]:checked')?.value; // commute, hobby


        if (!selectedActivity || !selectedType) {
            alert("Please select an activity and an activity type.");
            return;
        }

        // Send data to Django to store in database
        fetch("/log-activity/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()  // CSRF token function below
            },
            body: JSON.stringify({
                activity_id: selectedActivity, // Strava activity ID
                distance: selectedDistance, // Distance in meters
                activity_type: selectedType, // Activity type (walk, run, cycle)
                option: selectedOption // Activity option (commute, hobby)
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById("log-popup").style.display = "none";
                document.getElementById("success-popup").style.display = "flex";

                if (data.lootboxes_to_reward > 0) {
                    showLootboxesAwarded(3, data.lootboxes_to_reward);
                }

                updateStats();
                updateLeaderboard();
            } else {
                document.getElementById("log-popup").style.display = "none";
                document.getElementById("error-popup").style.display = "flex";
                console.error("Error logging activity:", data.error);
            }
        })
        .catch(error => console.error("Error logging activity:", error));
    });

    // Function to update stats on page
    function updateStats() {
        fetch("/get-transport-stats/")
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error("Error fetching stats:", data.error);
                    return;
                }

                const pointsEarned = document.getElementById("stats-points-earned");
                const totalDistance = document.getElementById("stats-total-distance");
                const emissionsReduced = document.getElementById("stats-emissions-reduced");

                // Update points
                pointsEarned.textContent = data.points_earned;
                // Update total distance ( add total commute and hobby distance)
                totalDistance.textContent = ((data.total_commute_distance + data.total_hobby_distance) / 1000).toFixed(2);
                // Update emissions reduced ( add total commute and hobby distance and calculate emissions) (1 km = 0.18kg CO2)
                emissionsReduced.textContent = ((data.total_commute_distance + data.total_hobby_distance) * 180 / 1000000).toFixed(2);
            })
            .catch(error => console.error("Error fetching stats:", error));
    }

    // Function to update leaderboard on page
    function updateLeaderboard() {
        fetch("/get-transport-leaderboard/")
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
                            leaderboardItem.textContent = `${data[i].username} - ${data[i].transport_points} pts`;
                        } else {
                            leaderboardItem.textContent = "---";  // Placeholder if no data
                        }
                    }
                }
            })
            .catch(error => console.error("Error fetching leaderboard:", error));
    }    

    // Function to get CSRF token from cookies
    function getCSRFToken() {
        const cookies = document.cookie.split("; ");
        for (let cookie of cookies) {
            const [name, value] = cookie.split("=");
            if (name === "csrftoken") return value;
        }
        return "";
    }

    // Close the log popup
    document.getElementById("close-log-popup").addEventListener("click", function() {
        document.getElementById("log-popup").style.display = "none";
    });

    // Close the success popup
    document.getElementById("close-success-popup").addEventListener("click", function() {
        document.getElementById("success-popup").style.display = "none";
    });

    // Close the error popup
    document.getElementById("close-error-popup").addEventListener("click", function() {
        document.getElementById("error-popup").style.display = "none";
    });

        // --------------------------------------------------
    // Lootbox popup
    // --------------------------------------------------

    function showLootboxesAwarded(lootbox_id, quantity) { // Pass in lootbox_id and quantity of lootboxes to show
        // Create div element for lootbox popup
        const lootboxPopup = document.createElement('div');
        lootboxPopup.id = 'lootbox-popup';
        
        // Create div element for lootbox content and append to popup
        const lootboxContent = document.createElement('div');
        lootboxContent.id = 'lootbox-content';
        lootboxPopup.appendChild(lootboxContent);
    
        // Make request to get lootbox data from views.py get_lootbox_data function
        fetch(`/get-lootbox-data/?lootbox_id=${lootbox_id}`)
        .then(response => response.json())
        .then(data => {
            // Create lootbox image element and append to lootbox content
            const lootboxImage = document.createElement('img');
            lootboxImage.src = data.lootbox_image;
            lootboxImage.alt = data.lootbox_name;
            lootboxContent.appendChild(lootboxImage);
    
            // Create lootbox name element and append to lootbox content
            const lootboxName = document.createElement('p');
            lootboxName.textContent = data.lootbox_name;
            lootboxContent.appendChild(lootboxName);
    
            // Create lootbox quantity element and append to lootbox content
            const lootboxQuantity = document.createElement('p');
            lootboxQuantity.textContent = `Quantity: ${quantity}`;
            lootboxContent.appendChild(lootboxQuantity);
    
            // Create lootbox close button and append to lootbox content
            const lootboxCloseBtn = document.createElement('button');
            lootboxCloseBtn.textContent = 'Close';
            lootboxCloseBtn.addEventListener('click', () => {
                lootboxPopup.remove();
            });
            lootboxContent.appendChild(lootboxCloseBtn);
    
            // Append the popup to the document so it becomes visible
            document.body.appendChild(lootboxPopup);
        })
        .catch(error => console.error("Error fetching lootbox data:", error));
    }


    // Fetch stats when page loads
    updateStats();
    updateLeaderboard();
});
