//On load, add event listeners to all open lootbox buttons
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".open-lootbox-btn").forEach(button => {
        button.addEventListener("click", function () {
            const lootboxId = this.getAttribute("data-item-id");
            console.log("Button clicked, lootbox id: ", lootboxId);
            openLootbox(lootboxId, this);
        });
    });
});

function openLootbox(lootboxId, button) {
    fetch(`/open-lootbox/${lootboxId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayLootboxResult(data.item_won, button, data.lootbox_removed);
        } else {
            alert(data.error || "Something went wrong!");
        }
    })
    .catch(error => console.error("Error:", error));
}

//NOTE - add fetch new data to update the inventory after opening a lootbox
function displayLootboxResult(item, button, lootboxRemoved) {
    // Create a pop-up message
    const popup = document.createElement("div");
    popup.classList.add("lootbox-popup");
    popup.innerHTML = `
        <h2>You won: ${item.name}!</h2>
        ${item.image ? `<img src="${item.image}" alt="${item.name}">` : ""}
        <p>${item.description || ""}</p>
        <button onclick="this.parentElement.remove()">Close</button>
    `;

    document.body.appendChild(popup);

    updateInventory();

}
    
function updateInventory() {
    fetch("/get-inventory/")
        .then(response => response.text())
        .then(html => {
            document.querySelector("#inventory-container").innerHTML = html;
            attachEventListeners();  //Add event listeners to remade buttons from getting new inventory
        })
        .catch(error => console.error("Error updating inventory:", error));
}

function attachEventListeners() {
    document.querySelectorAll(".open-lootbox-btn").forEach(button => {
        button.addEventListener("click", function () {
            const lootboxId = this.getAttribute("data-item-id");
            openLootbox(lootboxId, this);
        });
    });
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
