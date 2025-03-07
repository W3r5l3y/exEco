document.addEventListener("DOMContentLoaded", function () {
    // Function to update the countdown timers
    function updateCountdown(timerElement, deadline) {
        function calculateTimeLeft() {
            const now = new Date().getTime();
            const timeLeft = deadline - now;

            if (timeLeft <= 0) {
                if (timerElement) timerElement.innerHTML = "00:00:00"; // Reset when expired
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
                    timerElement.innerHTML = `${hours}:${minutes}:${seconds}`;
                }
            }
        }

        calculateTimeLeft();
        setInterval(calculateTimeLeft, 1000);
    }

    // Fix: Ensure these elements exist before using them
    const dailyTimer = document.getElementById("daily-timer");
    const weeklyTimer = document.getElementById("weekly-timer");

    // Set deadlines for daily and weekly challenges (next midnight and next Monday)
    const now = new Date();
    
    const dailyReset = new Date();
    dailyReset.setHours(24, 0, 0, 0); 

    const weeklyReset = new Date();
    weeklyReset.setDate(now.getDate() + (8 - now.getDay()) % 7);
    weeklyReset.setHours(0, 0, 0, 0);

    if (dailyTimer) updateCountdown(dailyTimer, dailyReset.getTime());
    if (weeklyTimer) updateCountdown(weeklyTimer, weeklyReset.getTime());

    // Update progress bars
    document.querySelectorAll(".progress-bar").forEach(bar => {
        let progressElement = bar.querySelector(".progress");
        let challengeItem = bar.closest(".challenge-item");

        if (progressElement && challengeItem) {
            let progressText = challengeItem.querySelector(".challenge-progress").innerText;
            let progressParts = progressText.match(/(\d+)\/(\d+)/);

            if (progressParts) {
                let currentProgress = parseInt(progressParts[1]);
                let goal = parseInt(progressParts[2]);
                let percentage = (currentProgress / goal) * 100;

                progressElement.style.width = `${percentage}%`;

                if (percentage >= 100) {
                    challengeItem.classList.add("completed");
                }
            }
        }
    });

    // Handle challenge submission
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
                    this.innerText = "Completed";
                    this.disabled = true;
                    this.style.backgroundColor = "#888";
                } else {
                    alert("Error submitting challenge. Try again later.");
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });

    // Function to get CSRF token
    function getCSRFToken() {
        return document.cookie.split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
    }
});
