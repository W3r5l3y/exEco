document.addEventListener("DOMContentLoaded", async () => {
    // Map to store garden state: key = "<row>-<col>", value = unique inventory item id
    const gardenState = new Map();

    const inventoryWrapper = document.querySelector("#inventory-wrapper");

    /* --------------------------------------------------
    *  Function to load inventory items from the server
    * -------------------------------------------------- */
    async function loadInventory() {
        try {
            const response = await fetch("/load-inventory/");
            const data = await response.json();
            if (data.items) {
                data.items.forEach(item => {
                    // Use the base id returned from the server (e.g., "inventory-item-123")
                    const baseId = item.id;
                    // Create a DOM element for each quantity
                    for (let i = 1; i <= item.quantity; i++) {
                        const uniqueId = `${baseId}-${i}`; // e.g., "inventory-item-123-1"
                        const inventoryItem = document.createElement("div");
                        inventoryItem.classList.add("inventory-item");
                        inventoryItem.id = uniqueId;
                        // Store the unique id in the dataset so that later we can refer to this specific instance.
                        inventoryItem.dataset.itemId = uniqueId;
    
                        const img = document.createElement("img");
                        img.src = item.img;
                        img.alt = item.name;
                        img.draggable = false; // Prevents dragging the image
    
                        const name = document.createElement("p");
                        name.textContent = item.name;
    
                        inventoryItem.appendChild(img);
                        inventoryItem.appendChild(name);
                        inventoryWrapper.appendChild(inventoryItem);
                    }
                });
                // Attach click event listeners to each dynamically loaded inventory item.
                document.querySelectorAll(".inventory-item").forEach(inventoryItem => {
                    inventoryItem.addEventListener("click", handleInventoryItemClick);
                });
            }
        } catch (error) {
            console.error("Error loading inventory:", error);
        }
    }

    /* --------------------------------------------------
    *  Function to load garden state from the server
    * -------------------------------------------------- */
    async function loadGardenState() {
        try {
            const response = await fetch("/load-garden/");
            const data = await response.json();
            if (data.state) {
                Object.entries(data.state).forEach(([key, uniqueItemId]) => {
                    const cell = document.querySelector(`.grid-item-${key}`);
                    if (cell) {
                        const img = cell.querySelector("img");
                        // Find the inventory item element with the unique id
                        const inventoryItem = document.querySelector(`#${uniqueItemId}`);
                        if (inventoryItem) {
                            // Use the inventory item image source for the garden cell.
                            const invImg = inventoryItem.querySelector("img");
                            img.src = invImg.src;
                            gardenState.set(key, uniqueItemId);
    
                            // Mark that specific inventory item as selected.
                            inventoryItem.classList.add("inventory-item-selected");
                        }
                    }
                });
                console.log("Garden loaded:", gardenState);
            }
        } catch (error) {
            console.error("Error loading garden state:", error);
        }
    }

    /* --------------------------------------------------
    *  Helper function to get CSRF token from cookies
    * -------------------------------------------------- */
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /* --------------------------------------------------
    *  Function to add click event listener to inventory items with functionality
    * -------------------------------------------------- */
    function handleInventoryItemClick() {
        // If no grid cell is selected, do nothing.
        const selectedGridItem = document.querySelector(".grid-item-selected");
        if (!selectedGridItem) return;
    
        const itemId = this.dataset.itemId;
    
        // Check if this inventory item instance is already placed in the garden.
        let placedGridKey = null;
        gardenState.forEach((value, key) => {
            if (value === itemId) {
                placedGridKey = key;
            }
        });
    
        if (placedGridKey) {
            // If the selected grid cell already contains this inventory item, remove it.
            if (`grid-item-${placedGridKey}` === selectedGridItem.classList[1]) {
                selectedGridItem.querySelector("img").src = "/static/img/empty.png";
                this.classList.remove("inventory-item-selected");
                gardenState.delete(placedGridKey);
                console.log("Removed from garden:", itemId, "at", placedGridKey);
                return;
            }
            // Otherwise, flash the grid cell to indicate this instance is already placed.
            const gridItem = document.querySelector(`.grid-item-${placedGridKey}`);
            if (gridItem) {
                gridItem.classList.add("grid-item-flash");
                setTimeout(() => gridItem.classList.remove("grid-item-flash"), 1000);
            }
        } else {
            // Place the inventory item instance in the selected grid cell.
            this.classList.add("inventory-item-selected");
            const selectedImage = selectedGridItem.querySelector("img");
    
            // Extract grid coordinates from the grid cell's class (e.g., "grid-item-3-4" becomes "3-4").
            let gridKey = selectedGridItem.className.match(/grid-item-(\d+)-(\d+)/);
            if (gridKey) {
                gridKey = `${gridKey[1]}-${gridKey[2]}`;
    
                // If there is already an item in this grid cell, unselect that instance.
                if (gardenState.has(gridKey)) {
                    const existingItemId = gardenState.get(gridKey);
                    const existingInventoryItem = document.getElementById(existingItemId);
                    if (existingInventoryItem) {
                        existingInventoryItem.classList.remove("inventory-item-selected");
                    }
                }
                // Update the garden state with the new unique inventory item instance.
                gardenState.set(gridKey, itemId);
            }
    
            // Update the grid cell's image to show the placed item.
            selectedImage.src = this.querySelector("img").src;
            console.log("Updated garden state:", gardenState);
        }
    }

    /* --------------------------------------------------
    *  Populate the garden grid
    * -------------------------------------------------- */
    const gardenWrapper = document.querySelector("#garden-wrapper");
    for (let row = 1; row <= 9; row++) {
        for (let col = 1; col <= 9; col++) {
            const cell = document.createElement("div");
            cell.classList.add("grid-item", `grid-item-${row}-${col}`);
    
            const image = document.createElement("img");
            image.src = "/static/img/empty.png";
            image.alt = "Empty";
            image.draggable = false;
            cell.appendChild(image);
    
            gardenWrapper.appendChild(cell);
        }
    }
    
    // Add click event listener to all grid cells to allow selection.
    const gridItems = document.querySelectorAll(".grid-item");
    gridItems.forEach(gridItem => {
        gridItem.addEventListener("click", () => {
            gridItems.forEach(item => item.classList.remove("grid-item-selected"));
            gridItem.classList.add("grid-item-selected");
        });
    });
    
    // Save the garden state to the server when the button is clicked and render the image.
    document.querySelector("#save-garden-button").addEventListener("click", async () => {
        const gardenStateData = Object.fromEntries(gardenState);
        console.log("Saving garden state:", gardenStateData);
        const csrftoken = getCookie('csrftoken');
        const userId = document.querySelector("body").dataset.userId;
        const tooltip = document.getElementById("save-tooltip");
    
        try {
            // First endpoint: save the garden state.
            const saveResponse = await fetch("/save-garden/", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                body: JSON.stringify({ state: gardenStateData }),
            });
            const saveData = await saveResponse.json();
            console.log(saveData.message);
            
            if (saveData.average_stats) {
                updateGardenStats(saveData.average_stats, saveData.total_stats);
            }
            
            // Second endpoint: render the garden image.
            const imageResponse = await fetch("/save-garden-as-image/", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken
                },
                body: JSON.stringify({ state: gardenStateData, user_id: userId }),
            });
            const imageData = await imageResponse.json();
            console.log(imageData.message);
    
            // Show success tooltip
            tooltip.textContent = "Garden saved successfully!";
            tooltip.classList.add("show");
            setTimeout(() => tooltip.classList.remove("show"), 3000);
        } catch (error) {
            console.error("Error saving garden image:", error);
    
            // Show error tooltip
            tooltip.textContent = "Error saving garden!";
            tooltip.classList.add("show");
            setTimeout(() => tooltip.classList.remove("show"), 3000);
        }
    });  
    
    function updateGardenStats(stats, totalStat) {
        document.getElementById("garden-stat-1").textContent = stats.aesthetic_appeal.toFixed(1);
        document.getElementById("garden-stat-2").textContent = stats.habitat.toFixed(1);
        document.getElementById("garden-stat-3").textContent = stats.carbon_uptake.toFixed(1);
        document.getElementById("garden-stat-4").textContent = stats.waste_reduction.toFixed(1);
        document.getElementById("garden-stat-5").textContent = stats.health_of_garden.toFixed(1);
        document.getElementById("garden-stat-6").textContent = stats.innovation.toFixed(1);
        document.getElementById("garden-total-stat").textContent = totalStat.toFixed(1);
    }
    

    // Add reset garden functionality
document.querySelector("#reset-garden-button").addEventListener("click", async () => {
    // Clear the in-memory garden state.
    gardenState.clear();

    // Loop through all grid cells and set them to the empty image,
    // except cell 5-5 if you want to keep your tree there.
    document.querySelectorAll(".grid-item").forEach(cell => {
        if (!cell.classList.contains("grid-item-5-5")) {
            const img = cell.querySelector("img");
            if (img) {
                img.src = "/static/img/empty.png";
            }
        }
    });

    
    document.querySelectorAll(".inventory-item").forEach(item => {
        item.classList.remove("inventory-item-selected");
    });

    
    try {
        const csrftoken = getCookie('csrftoken');
        const response = await fetch("/save-garden/", {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify({ state: {} }),
        });
        const data = await response.json();
        console.log("Garden reset:", data);
        // Show a success tooltip
        const tooltip = document.getElementById("reset-tooltip");
        tooltip.textContent = "Garden reset successfully!";
        tooltip.classList.add("show");
        setTimeout(() => tooltip.classList.remove("show"), 3000);
    } catch (error) {
        console.error("Error resetting garden on server:", error);
        const tooltip = document.getElementById("reset-tooltip");
        tooltip.textContent = "Error resetting garden!";
        tooltip.classList.add("show");
        setTimeout(() => tooltip.classList.remove("show"), 3000);
    }
    });

    
    // Set the tree image in the center of the garden (cell 5,5).
    const gridItem55 = document.querySelector(".grid-item-5-5");
    const treeImage = gridItem55.querySelector("img");
    treeImage.src = "/static/img/temp-tree.png";
    
    // Load inventory first, then load the garden state so the selected instances are correctly marked.
    await loadInventory();
    await loadGardenState();
});
