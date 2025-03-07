document.addEventListener("DOMContentLoaded", function () {
    // Function to update the countdown timers
    function updateCountdown(timerElement, deadline) {
        function calculateTimeLeft() {
            const now = new Date().getTime();
            const timeLeft = deadline - now;

            if (timeLeft <= 0) {
                timerElement.innerHTML = "00:00:00"; // Reset when expired
                return;
            }

            const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

            if (days > 0) {
                timerElement.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;
            } else {
                timerElement.innerHTML = `${hours}:${minutes}:${seconds}`;
            }
        }

        calculateTimeLeft();
        setInterval(calculateTimeLeft, 1000);
    }

    // Set deadlines for daily and weekly challenges (next midnight and next Monday)
    const now = new Date();
    
    // Daily Challenge Reset at midnight
    const dailyReset = new Date();
    dailyReset.setHours(24, 0, 0, 0); 

    // Weekly Challenge Reset next Monday at midnight
    const weeklyReset = new Date();
    weeklyReset.setDate(now.getDate() + (8 - now.getDay()) % 7); // Next Monday
    weeklyReset.setHours(0, 0, 0, 0);

    updateCountdown(document.getElementById("daily-timer"), dailyReset.getTime());
    updateCountdown(document.getElementById("weekly-timer"), weeklyReset.getTime());

    // Handling challenge submission
    function handleChallengeSubmission(button) {
        const challengeId = button.getAttribute("data-challenge-id");

        fetch("/submit-challenge/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken() // CSRF Protection
            },
            body: JSON.stringify({ challenge_id: challengeId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                button.innerText = "Completed";
                button.disabled = true;
                button.style.backgroundColor = "#888";
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => console.error("Error:", error));
    }

    // Add event listeners to all submit buttons
    document.querySelectorAll(".submit-btn").forEach(button => {
        button.addEventListener("click", function () {
            handleChallengeSubmission(this);
        });
    });

    // Function to get CSRF token for Django security
    function getCSRFToken() {
        return document.cookie.split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
    }
});
