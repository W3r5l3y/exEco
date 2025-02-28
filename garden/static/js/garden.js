document.addEventListener("DOMContentLoaded", () => {
    // Get the garden wrapper element and add the grid items
    const gardenWrapper = document.querySelector("#garden-wrapper");
    for (let row = 1; row <= 9; row++) {
        for (let col = 1; col <= 9; col++) {
            const cell = document.createElement("div");
            cell.classList.add("grid-item", `grid-item-${row}-${col}`);

            const image = document.createElement("img");
            image.src = "/static/img/empty.png";
            cell.appendChild(image);

            gardenWrapper.appendChild(cell);
        }
    }

    // Set the image of the tree in the center of the garden (5, 5)
    const gridItem55 = document.querySelector(".grid-item-5-5");
    const treeImage = gridItem55.querySelector("img");
    treeImage.src = "/static/img/temp-tree.png";
});