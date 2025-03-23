document.addEventListener("DOMContentLoaded", function () {
    function updateCountdown(timerElement, deadline) {
        function calculateTimeLeft() {
            const now = new Date().getTime();
            const timeLeft = deadline - now;

            if (timeLeft <= 0) {
                if (timerElement) timerElement.innerHTML = "00:00:00";
                return;
            }

            const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

            if (timerElement) {
                if (days > 0) {
                    timerElement.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;
                } else {
                    timerElement.innerHTML = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                }
            }
        }

        calculateTimeLeft();
        return setInterval(calculateTimeLeft, 1000);
    }

    const dailyTimer = document.getElementById("daily-timer");
    const weeklyTimer = document.getElementById("weekly-timer");

    // Flag to determine if timers are already set
    let timersSet = false;

    // Try to fetch reset times from the server
    fetch("/get-reset-times/")
    .then(response => response.json())
    .then(data => {
        if (dailyTimer && data.daily_reset) {
            const dailyResetTime = new Date(data.daily_reset);
            dailyResetTime.setDate(dailyResetTime.getDate() + 1); // Next reset
            updateCountdown(dailyTimer, dailyResetTime.getTime());
            timersSet = true;
        }
        if (weeklyTimer && data.weekly_reset) {
            const weeklyResetTime = new Date(data.weekly_reset);
            weeklyResetTime.setDate(weeklyResetTime.getDate() + 7); // Next reset
            updateCountdown(weeklyTimer, weeklyResetTime.getTime());
            timersSet = true;
        }
    })
    .catch(error => {
        console.error("Error fetching reset times:", error);
    })
    .finally(() => {
        // If timers weren't set from the server, fall back to static deadlines.
        if (!timersSet) {
            const now = new Date();
            
            if (dailyTimer) {
                const dailyReset = new Date();
                dailyReset.setHours(0, 0, 0, 0);
                dailyReset.setDate(dailyReset.getDate() + 1); 
                updateCountdown(dailyTimer, dailyReset.getTime());
            }
    
            if (weeklyTimer) {
                const weeklyReset = new Date();
                // Calculate days until next Monday (assuming Monday is the weekly reset)
                weeklyReset.setDate(now.getDate() + ((8 - now.getDay()) % 7));
                weeklyReset.setHours(0, 0, 0, 0);
                updateCountdown(weeklyTimer, weeklyReset.getTime());
            }
        }
    });

    // Handle challenge submission logic
    document.querySelectorAll(".submit-btn").forEach(button => {
        button.addEventListener("click", function () {
            const challengeId = this.getAttribute("data-challenge-id");

            fetch("/submit-challenge/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({ challenge_id: challengeId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const challengeItem = this.closest(".challenge-item");
                    const progressText = challengeItem.querySelector(".challenge-progress");
            
                    if (data.progress !== undefined && data.goal !== undefined) {
                        progressText.textContent = `Progress: ${data.progress}/${data.goal}`;
                    }
            
                    if (data.completed) {
                        this.innerText = "Completed";
                        this.disabled = true;
                        challengeItem.classList.add("completed");
                    }
                } else {
                    alert("Error submitting challenge. Try again later.");
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });

    // Function to get CSRF token
    function getCSRFToken() {
        let cookieValue = null;
        document.cookie.split("; ").forEach(row => {
            if (row.startsWith("csrftoken=")) {
                cookieValue = row.split("=")[1];
            }
        });
        return cookieValue;
    }
});