document.addEventListener("DOMContentLoaded", () => {
    const gardenWrapper = document.querySelector(".garden-wrapper");

    for (let row = 1; row <= 9; row++) {
        for (let col = 1; col <= 9; col++) {
            const cell = document.createElement("div");
            cell.classList.add("grid-item", `grid-item-${row}-${col}`);
            cell.textContent = `${row},${col}`; // For debugging

            gardenWrapper.appendChild(cell);
        }
    }
});