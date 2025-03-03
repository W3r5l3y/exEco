document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".buy-item-btn").forEach(button => {
        button.addEventListener("click", function () {
            const shopItemId = this.getAttribute("data-item-id");
            buyItem(shopItemId, this);
        });
    });
});

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

function getCSRFToken() {
    const cookies = document.cookie.split("; ");
    for (let cookie of cookies) {
        if (cookie.startsWith("csrftoken=")) {
            return cookie.split("=")[1];
        }
    }
    return "";
}
