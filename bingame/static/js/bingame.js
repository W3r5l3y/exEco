document.addEventListener("DOMContentLoaded", function () {
    const draggables = document.querySelectorAll(".draggable");
    const bins = document.querySelectorAll(".bin");
    const checkButton = document.getElementById("check-answer-tile");
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
            let binId = bin.id;

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

    checkButton.addEventListener("click", () => {
        let allCorrect = true;

        for (let itemId in placedItems) {
            let correctBin = document.getElementById(itemId).dataset.correctBin;
            let placedBin = placedItems[itemId];

            if (placedBin !== correctBin) {
                allCorrect = false;
                break;
            }
        }

        // Display feedback message
        feedback.innerText = allCorrect ? "✅ Correct! All items are in the right bins!" : "❌ Some items are in the wrong bins!";
        feedback.style.position = "fixed";
        feedback.style.bottom = "80px";
        feedback.style.right = "20px";
        feedback.style.padding = "15px";
        feedback.style.backgroundColor = allCorrect ? "#4CAF50" : "#FF3333";
        feedback.style.color = "white";
        feedback.style.borderRadius = "10px";
        feedback.style.fontWeight = "bold";
    });
});
