document.addEventListener("DOMContentLoaded", async function () {
    try {
        // Ensure new challenges are assigned before fetching them
        await fetch("/api/assign_challenges/", { method: "GET", credentials: "same-origin" });
        
        const response = await fetch("/api/challenges/", { method: "GET", credentials: "same-origin" });
        const data = await response.json();

        const dailyContainer = document.getElementById("daily-challenges");
        const weeklyContainer = document.getElementById("weekly-challenges");

        dailyContainer.innerHTML = ""; // Clear existing content
        weeklyContainer.innerHTML = "";

        // Populate daily challenges
        data.daily.forEach(challenge => {
            const challengeElement = document.createElement("div");
            challengeElement.classList.add("daily-challenge");
            challengeElement.innerHTML = `
                <p>${challenge.description}</p>
                <p>${challenge.points} Points</p>
                <button onclick="submitChallenge('${challenge.id}')">Submit</button>
            `;
            dailyContainer.appendChild(challengeElement);
        });

        // Populate weekly challenges
        data.weekly.forEach(challenge => {
            const challengeElement = document.createElement("div");
            challengeElement.classList.add("weekly-challenge");
            challengeElement.innerHTML = `
                <p>${challenge.description}</p>
                <p>${challenge.points} Points</p>
                <button onclick="submitChallenge('${challenge.id}')">Submit</button>
            `;
            weeklyContainer.appendChild(challengeElement);
        });
    } catch (error) {
        console.error("Error fetching challenges:", error);
    }
});

// Function to handle challenge submission
async function submitChallenge(challengeId) {
    try {
        const response = await fetch("/api/submit_challenge/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken() // Ensure CSRF token is included
            },
            body: JSON.stringify({ challenge_id: challengeId })
        });
        const result = await response.json();
        alert(result.message);
    } catch (error) {
        console.error("Error submitting challenge:", error);
    }
}

// Helper function to get CSRF token
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith("csrftoken=")) {
            return cookie.substring("csrftoken=".length, cookie.length);
        }
    }
    return "";
}
