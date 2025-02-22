document.addEventListener("DOMContentLoaded", function() {
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
        fetch("/get-stats/")
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




    // Fetch stats when page loads
    updateStats();
    updateLeaderboard();
});
