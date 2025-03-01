document.addEventListener("DOMContentLoaded", () => {
    // Map to store garden state
    const gardenState = new Map(); // key: <row>-<col>, value: inventory item id

    // Inventory items (will be loaded dynamically in the future)
    const inventoryItemsData = [
        { id: "inventory-item-1", src: "/static/img/temp-leaf.png", name: "Temp 1" },
        { id: "inventory-item-2", src: "/static/img/temp-leaf.png", name: "Temp 2" },
        { id: "inventory-item-3", src: "/static/img/temp-leaf.png", name: "Temp 3" }
    ];

    // Populate inventory
    const inventoryWrapper = document.querySelector("#inventory-wrapper");
    inventoryItemsData.forEach(item => {
        const inventoryItem = document.createElement("div");
        inventoryItem.classList.add("inventory-item");
        inventoryItem.id = item.id;
        inventoryItem.dataset.itemId = item.id; // Store item ID for interactions

        const img = document.createElement("img");
        img.src = item.src;
        img.alt = item.name;
        img.draggable = false; // Prevents dragging the image

        const name = document.createElement("p");
        name.textContent = item.name;

        inventoryItem.appendChild(img);
        inventoryItem.appendChild(name);
        inventoryWrapper.appendChild(inventoryItem);
    });

    // Populate garden grid
    const gardenWrapper = document.querySelector("#garden-wrapper");
    for (let row = 1; row <= 9; row++) {
        for (let col = 1; col <= 9; col++) {
            const cell = document.createElement("div");
            cell.classList.add("grid-item", `grid-item-${row}-${col}`);

            const image = document.createElement("img");
            image.src = "/static/img/empty.png";
            image.alt = "Empty";
            image.draggable = false; // Prevents dragging the image
            cell.appendChild(image);

            gardenWrapper.appendChild(cell);
        }
    }

    // Set the image of the tree in the center of the garden (5, 5)
    const gridItem55 = document.querySelector(".grid-item-5-5");
    const treeImage = gridItem55.querySelector("img");
    treeImage.src = "/static/img/temp-tree.png";

    // Add click event listener to all grid items
    const gridItems = document.querySelectorAll(".grid-item");
    gridItems.forEach(gridItem => {
        gridItem.addEventListener("click", () => {
            gridItems.forEach(item => item.classList.remove("grid-item-selected"));
            gridItem.classList.add("grid-item-selected");
        });
    });

    // Add click event listener to inventory items
    document.querySelectorAll(".inventory-item").forEach(inventoryItem => {
        inventoryItem.addEventListener("click", () => {
            // If no grid item is selected, do nothing
            const selectedGridItem = document.querySelector(".grid-item-selected");
            if (!selectedGridItem) return;
            
            const itemId = inventoryItem.dataset.itemId;
            
            // Find if this item is already placed in the garden
            let placedGridKey = null;
            gardenState.forEach((value, key) => {
                if (value === itemId) {
                    placedGridKey = key; // Find the grid cell where this item is placed
                }
            });

            if (placedGridKey) {
                // If this inventory item is already placed, check if the user selected that grid item
                const selectedGridItem = document.querySelector(".grid-item-selected");
                if (selectedGridItem && selectedGridItem.classList.contains(`grid-item-${placedGridKey}`)) {
                    // If the user selected the grid item containing this inventory item, remove it
                    selectedGridItem.querySelector("img").src = "/static/img/empty.png";
                    inventoryItem.classList.remove("inventory-item-selected");
                    gardenState.delete(placedGridKey);
                    console.log("Removed from garden:", itemId, "at", placedGridKey);
                    return;
                }

                // Otherwise, flash the existing grid item to indicate it's already placed
                const gridItem = document.querySelector(`.grid-item-${placedGridKey}`);
                if (gridItem) {
                    gridItem.classList.add("grid-item-flash");
                    setTimeout(() => gridItem.classList.remove("grid-item-flash"), 1000);
                }
            } else {
                // If item is not placed, allow placing it
                inventoryItem.classList.add("inventory-item-selected");

                const selectedGridItem = document.querySelector(".grid-item-selected");
                if (!selectedGridItem) return; // No grid item selected

                const selectedImage = selectedGridItem.querySelector("img");

                // Get row and col from the grid item's class
                let gridKey = selectedGridItem.className.match(/grid-item-(\d+)-(\d+)/);
                if (gridKey) {
                    gridKey = `${gridKey[1]}-${gridKey[2]}`;

                    // Check if there is already an item in the selected grid slot
                    if (gardenState.has(gridKey)) {
                        const existingItemId = gardenState.get(gridKey);
                        const existingInventoryItem = document.getElementById(existingItemId);

                        if (existingInventoryItem) {
                            existingInventoryItem.classList.remove("inventory-item-selected");
                        }
                    }

                    // Update the garden state with the new item
                    gardenState.set(gridKey, itemId);
                }

                // Set the selected grid item image
                selectedImage.src = inventoryItem.querySelector("img").src;

                console.log("Updated garden state:", gardenState);
            }
        });
    });

    // Add click event listener to save button
    const saveButton = document.querySelector("#save-garden-button");
    saveButton.addEventListener("click", () => {
        console.log("Saving garden state:", gardenState);

        // TODO: Send the garden state to the server
    });
});