document.addEventListener("DOMContentLoaded", function () {
    const draggables = document.querySelectorAll(".draggable");
    const bins = document.querySelectorAll(".bin");
    const checkButton = document.getElementById("check-answer-tile");
    const resetButton = document.getElementById("reset-game-tile");
    const feedback = document.createElement("div"); // Feedback message container

    let placedItems = {}; // Store which item is placed in which bin

    feedback.id = "feedback";
    document.body.appendChild(feedback); // Add feedback message

    draggables.forEach(item => {
        item.draggable = true;
        item.addEventListener("dragstart", (event) => {
            event.dataTransfer.setData("item-id", event.target.id);
            event.dataTransfer.setData("correct-bin", event.target.dataset.correctBin);
        });
    });

    bins.forEach(bin => {
        bin.addEventListener("dragover", (event) => event.preventDefault());

        bin.addEventListener("drop", (event) => {
            event.preventDefault();
            const itemId = event.dataTransfer.getData("item-id");
            const correctBin = event.dataTransfer.getData("correct-bin");

            let draggedItem = document.getElementById(itemId);
            let binId = bin.dataset.binId; // Using data-bin-id from the HTML

            // Attach the item to the bin
            if (draggedItem) {
                bin.appendChild(draggedItem);
                draggedItem.style.position = "relative";
                draggedItem.style.margin = "5px";

                // Store the placed item
                placedItems[itemId] = binId;
            }
        });
    });

    // Ensure the check button calls `checkAnswers()`
    checkButton.addEventListener("click", checkAnswers);
    
    // Ensure the reset button calls `resetGame()`
    resetButton.addEventListener("click", resetGame);
});

// Function to check if the placed items are correct
function checkAnswers() {
    let allCorrect = true;

    for (let itemId in placedItems) {
        let itemElement = document.getElementById(itemId);
        let correctBinId = itemElement.dataset.correctBin; // Bin ID from database
        let placedBinId = placedItems[itemId];

        if (placedBinId !== correctBinId) {
            allCorrect = false;
            break;
        }
    }

    // Display feedback message
    const feedback = document.getElementById("feedback") || document.createElement("div");
    feedback.id = "feedback";
    feedback.innerText = allCorrect ? "✅ Correct! All items are in the right bins!" : "❌ Some items are in the wrong bins!";
    feedback.style.position = "fixed";
    feedback.style.bottom = "80px";
    feedback.style.right = "20px";
    feedback.style.padding = "15px";
    feedback.style.backgroundColor = allCorrect ? "#4CAF50" : "#FF3333";
    feedback.style.color = "white";
    feedback.style.borderRadius = "10px";
    feedback.style.fontWeight = "bold";

    document.body.appendChild(feedback);
}

// Function to reset the game
function resetGame() {
    const itemsContainer = document.getElementById("items-container");
    const items = document.querySelectorAll(".draggable");

    // Move all items back to the original container
    items.forEach(item => {
        itemsContainer.appendChild(item);
        item.style.position = "relative"; // Reset any positioning
        item.style.margin = "5px"; // Reset spacing
    });

    // Clear stored placements
    placedItems = {};

    // Remove feedback message if it exists
    const feedback = document.getElementById("feedback");
    if (feedback) {
        feedback.innerText = "";
    }
}
