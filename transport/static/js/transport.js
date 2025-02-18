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
                    select.appendChild(option);
                });
            })
            .catch(error => console.error("Error fetching activities:", error));
    });

    document.getElementById("submit-activity").addEventListener("click", function() {
        const selectedActivity = document.getElementById("activity-select").value;
        const selectedOption = document.querySelector("#activity-select option:checked");
        const selectedDistance = selectedOption ? selectedOption.dataset.distance : null;
        const selectedType = document.querySelector('input[name="activity-type"]:checked')?.value;

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
                activity_id: selectedActivity,
                distance: selectedDistance,
                activity_type: selectedType
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Activity logged successfully!");
                document.getElementById("log-popup").style.display = "none";
            } else {
                alert("Error logging activity: " + data.error);
            }
        })
        .catch(error => console.error("Error logging activity:", error));
    });

    // Function to get CSRF token from cookies
    function getCSRFToken() {
        const cookies = document.cookie.split("; ");
        for (let cookie of cookies) {
            const [name, value] = cookie.split("=");
            if (name === "csrftoken") return value;
        }
        return "";
    }
});
