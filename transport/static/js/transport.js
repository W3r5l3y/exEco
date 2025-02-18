document.getElementById("fetch-activity-btn").addEventListener("click", function() {
    fetch("{% url 'get-latest-activity' %}")
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById("activity-result").innerHTML = `<p>Error: ${data.error}</p>`;
            } else {
                document.getElementById("activity-result").innerHTML = `
                    <h3>Latest Activity: ${data.name}</h3>
                    <p>Distance: ${data.distance} meters</p>
                    <p>Time: ${data.moving_time} seconds</p>
                    <p>Type: ${data.type}</p>
                `;
            }
        })
        .catch(error => {
            document.getElementById("activity-result").innerHTML = `<p>Error fetching activity.</p>`;
        });
});