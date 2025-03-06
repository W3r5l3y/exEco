document.addEventListener("DOMContentLoaded", function () {
    // Select all shop items and modal elements
    const shopItems = document.querySelectorAll('.shop-item');
    const shopModal = document.querySelector('.shop-modal');
    const shopModalItemImg = document.querySelector('.shop-modal-item-img');
    const shopModalItemName = document.querySelector('.shop-modal-item-name');
    const shopModalItemDesc = document.querySelector('.shop-modal-item-desc');
    const shopModalItemCost = document.querySelector('.shop-modal-item-cost');
    const modalCloseBtn = document.querySelector('.shop-modal-close-btn');

    // Add click event to each shop item
    shopItems.forEach(item => {
        item.addEventListener('click', () => {
            // Get the item's details from the data attributes
            const itemId = item.dataset.itemId;
            const itemName = item.dataset.itemName;
            const itemDesc = item.dataset.itemDesc;
            const itemCost = item.dataset.itemCost;
            const itemImgSrc = item.dataset.itemImgSrc;

            // Update modal content with the item's details
            shopModalItemImg.src = itemImgSrc;
            shopModalItemName.textContent = itemName;
            shopModalItemDesc.textContent = itemDesc;
            shopModalItemCost.textContent = itemCost;

            // Display the modal
            shopModal.classList.add('active');

            // Add event listener to the buy button
            const buyBtn = document.querySelector('.shop-modal-purchase-btn');
            buyBtn.addEventListener('click', () => {
                buyItem(itemId, buyBtn);
            });
        });
    });

    // Close modal when the close button is clicked
    modalCloseBtn.addEventListener('click', () => {
        shopModal.classList.remove('active');
    });

    // Close modal when the user clicks outside the modal
    shopModal.addEventListener('click', (e) => {
        if (e.target === shopModal) {
            shopModal.classList.remove('active');
        }
    });

    /* --------------------------------------------------
        Function to buy an item from the shop
    -------------------------------------------------- */
    function buyItem(shopItemId, button) {
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
                showTooltip("Item purchased successfully!", button);
            } else if (data.lowbalance) {
                showTooltip("Low Balance", button);
            } else {
                showTooltip(data.error || "Purchase failed!", button);
            }
        })
        .catch(error => {
            console.error("Error purchasing item:", error);
            showTooltip("Error purchasing item!", button);
        });
    }
    
    /* --------------------------------------------------
        Function to get the CSRF token from cookies
    -------------------------------------------------- */
    function getCSRFToken() {
        const cookies = document.cookie.split("; ");
        for (let cookie of cookies) {
            if (cookie.startsWith("csrftoken=")) {
                return cookie.split("=")[1];
            }
        }
        return "";
    }

    /* --------------------------------------------------
        Function to show a tooltip above the button
    -------------------------------------------------- */
    function showTooltip(message, buttonElement) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = message;
        document.body.appendChild(tooltip);

        // Get button position and tooltip dimensions
        const btnRect = buttonElement.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();

        // Calculate position for the tooltip
        const top = btnRect.top - tooltipRect.height - 5;
        const left = btnRect.left + (btnRect.width / 2) - (tooltipRect.width / 2);
        tooltip.style.top = top + 'px';
        tooltip.style.left = left + 'px';

        tooltip.style.opacity = '1';

        setTimeout(() => {
            tooltip.style.opacity = '0';
            setTimeout(() => {
                tooltip.remove();
            }, 300);
        }, 2000);
    }

    /* --------------------------------------------------
        Add event listeners to scroll buttons (existing functionality)
    -------------------------------------------------- */
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