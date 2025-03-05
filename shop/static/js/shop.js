document.addEventListener("DOMContentLoaded", function () {
    // Add event listeners to all buy item buttons
    document.querySelectorAll(".buy-item-btn").forEach(button => {
        button.addEventListener("click", function () {
            const shopItemId = this.getAttribute("data-item-id");
            buyItem(shopItemId, this);
        });
    });

    // Function to buy an item
    function buyItem(shopItemId, button) {
        console.log("Button clicked, shop item id: ", shopItemId);
        fetch(`/buy-item/${shopItemId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Item purchased successfully!");
            } else if(data.lowbalance){
                alert("LOW BALANCE");//Handle low balance
            } else {
                alert(data.error || "Purchase failed!");
            }
        })
        .catch(error => console.error("Error purchasing item:", error));
    }
    
    // Function to get the CSRF token
    function getCSRFToken() {
        const cookies = document.cookie.split("; ");
        for (let cookie of cookies) {
            if (cookie.startsWith("csrftoken=")) {
                return cookie.split("=")[1];
            }
        }
        return "";
    }

    // Setup scroll buttons
    const shopGrid = document.querySelector(".shop-items-grid");
    const scrollUpBtn = document.getElementById("scroll-up-btn");
    const scrollDownBtn = document.getElementById("scroll-down-btn");
    const scrollAmount = 220;

    scrollUpBtn.addEventListener("click", function () {
        shopGrid.scrollBy({ top: -scrollAmount, behavior: "smooth" });
    });
    scrollDownBtn.addEventListener("click", function () {
        shopGrid.scrollBy({ top: scrollAmount, behavior: "smooth" });
    });
});