document.addEventListener('DOMContentLoaded', () => {
    // --- Global variables ---
    let selectedItem = null;
    let attempts = 0;
    let score = 0;
    const maxAttempts = 3;
    const itemsContainer = document.getElementById('items-container');
    const bins = document.querySelectorAll('.bin');

    // --- CSRF Token ---
    function getCSRFToken() {
        const cookies = document.cookie.split("; ");
        for (let cookie of cookies) {
            const [name, value] = cookie.split("=");
            if (name === "csrftoken") return value;
        }
        return "";
    }

    // --- Selection Helpers ---
    // Clear the currently selected item and remove visual prompts
    function clearSelection() {
        if (selectedItem) {
            selectedItem.classList.remove('item-selected');
            selectedItem = null;
        }
        bins.forEach(bin => bin.classList.remove('bin-selectable'));
        itemsContainer.classList.remove('bin-selectable');
    }

    // When an item is clicked, select it and mark destinations as selectable
    function itemClickHandler(e) {
        // Prevent the click from propagating upward (to avoid triggering destination clicks immediately)
        e.stopPropagation();
        clearSelection();
        selectedItem = e.currentTarget;
        selectedItem.classList.add('item-selected');
        // Mark all possible destinations
        bins.forEach(bin => bin.classList.add('bin-selectable'));
        itemsContainer.classList.add('bin-selectable');
    }

    // When a destination (a bin or the items container) is clicked, move the selected item there
    function destinationClickHandler(e) {
        // Stop propagation so that nested clicks don't conflict
        e.stopPropagation();
        if (!selectedItem) return;
        const destination = e.currentTarget;
        // If a bin was clicked, move the item into that bin’s .bin-items container.
        if (destination.classList.contains('bin')) {
            const binId = destination.getAttribute('data-bin-id');
            if (binId) {
                selectedItem.setAttribute('data-dropped-bin-id', binId);
            }
            const binItemsContainer = destination.querySelector('.bin-items');
            if (binItemsContainer) {
                binItemsContainer.appendChild(selectedItem);
                // Reset positioning so CSS layout (grid or flex) handles the item
                selectedItem.style.position = 'static';
                selectedItem.style.left = '';
                selectedItem.style.top = '';
                selectedItem.style.transform = '';
            }
        }
        // If the items container is clicked, move the item back there (resetting its position)
        else if (destination.id === 'items-container') {
            selectedItem.removeAttribute('data-dropped-bin-id');
            itemsContainer.appendChild(selectedItem);
            selectedItem.style.position = 'static';
        }
        clearSelection();
    }

    // --- Binding Functions ---
    // Bind click events to all items so that they can be selected
    function bindItemClickListeners() {
        document.querySelectorAll('.items').forEach(item => {
            // (Optional) Save original positioning if needed
            // item.dataset.originalLeft = ... ; item.dataset.originalTop = ... ;
            item.addEventListener('click', itemClickHandler);
        });
    }

    // Bind destination click events to bins and the items container
    function bindDestinationListeners() {
        bins.forEach(bin => {
            bin.addEventListener('click', destinationClickHandler);
        });
        itemsContainer.addEventListener('click', destinationClickHandler);
    }

    // Rebind item listeners (called after items are reloaded)
    function rebindItemEventListeners() {
        bindItemClickListeners();
        // Prevent image dragging
        document.querySelectorAll('.items img').forEach(img => {
            img.ondragstart = (e) => e.preventDefault();
        });
    }

    // --- (Unused Drag Functions Removed) ---
    // (mouseDown, mouseMove, mouseUp have been removed since we now use clicks.)

    // --- Answer Checking and Game Functions ---
    function resetItemPosition(item) {
        item.style.removeProperty('left');
        item.style.removeProperty('top');
        item.style.removeProperty('transform');
        item.style.removeProperty('position'); 
        item.removeAttribute('data-dropped-bin-id');
    }

    function checkAnswers() {
        const items = document.querySelectorAll('.items');
        const totalItems = items.length;
        let allPlaced = true;
    
        // Check if every item is placed; if not, mark it with a dashed red border.
        items.forEach(item => {
            if (!item.getAttribute('data-dropped-bin-id')) {
                allPlaced = false;
                item.style.border = '2px solid rgb(240, 152, 149)';
            }
        });
    
        if (!allPlaced) {
            alert('Please place all items in the correct bins');
            return;
        }
    
        attempts++;
    
        let correctCount = 0;
        items.forEach(item => {
            const correctBinId = item.getAttribute('data-correct-bin-id');
            const droppedBinId = item.getAttribute('data-dropped-bin-id');
    
            if (correctBinId === droppedBinId) {
                correctCount++;
                item.classList.add('correct');
            } else {
                // Incorrect item: remove incorrect styles, reset its position, and move it back.
                item.classList.remove('correct');
                resetItemPosition(item);
                item.style.border = '2px solid rgb(240, 152, 149)';
                item.removeAttribute('data-dropped-bin-id');
                itemsContainer.appendChild(item);
            }
        });
    
        if (correctCount === totalItems || attempts >= maxAttempts) {
            let tempScore = calculateScore();
            endGame(tempScore);
        }
    
        const attemptsLeftElem = document.getElementById('attempts-left');
        if (attemptsLeftElem) {
            attemptsLeftElem.innerText = `Attempts left: ${maxAttempts - attempts}`;
        }
    }    

    function calculateScore() {
        if (attempts >= maxAttempts) {
            return 0;
        }
        let points = (maxAttempts - attempts + 1) * 2;
        score += points;
        return score;
    }

    function endGame(tempScore) {
        updateLeaderboard(tempScore);
    
        const itemsContainer = document.getElementById('items-container');
        const checkAnswerBtn = document.getElementById('check-answer-tile');
        const attemptsLeftElem = document.getElementById('attempts-left');
    
        // Clear the main items container
        itemsContainer.innerHTML = '';
    
        // Also clear all items that might have been placed into bins
        document.querySelectorAll('.bin .bin-items').forEach(binItemsContainer => {
            binItemsContainer.innerHTML = '';
        });
    
        // Create and show result message
        const resultMessage = document.createElement('p');
        resultMessage.style.fontSize = '24px';
        resultMessage.style.fontWeight = 'bold';
        resultMessage.style.textAlign = 'center';
        resultMessage.style.marginTop = '50px';
    
        if (tempScore > 0) {
            itemsContainer.style.backgroundColor = 'lightgreen'; // Win
            resultMessage.textContent = `Game Won! Score: ${tempScore}`;
        } else {
            itemsContainer.style.backgroundColor = 'lightcoral'; // Lose
            resultMessage.textContent = `Game Lost!`;
        }
    
        itemsContainer.appendChild(resultMessage);
        
        document.getElementById('check-answer-label').innerText = 'Next Round';
        checkAnswerBtn.removeEventListener('click', checkAnswers);
        checkAnswerBtn.addEventListener('click', resetGame);
    }
    
    function resetGame() {
        attempts = 0;
        score = 0;
    
        const itemsContainer = document.getElementById('items-container');
        const checkAnswerBtn = document.getElementById('check-answer-tile');
        const attemptsLeftElem = document.getElementById('attempts-left');
        
        // Reset the items container styling and clear its content
        itemsContainer.style.backgroundColor = '';
        itemsContainer.innerHTML = '';
    
        // Clear any items that might be in the bin-items containers
        document.querySelectorAll('.bin .bin-items').forEach(container => {
            container.innerHTML = '';
        });
    
        getLeaderboard();
        fetchNewRandomItems();
    
        document.getElementById('check-answer-label').innerText = 'Check Answers';
        checkAnswerBtn.removeEventListener('click', resetGame);
        checkAnswerBtn.addEventListener('click', checkAnswers);
    
        if (attemptsLeftElem) {
            attemptsLeftElem.style.display = 'block';
            attemptsLeftElem.innerText = `Attempts left: ${maxAttempts - attempts}`;
        }
    }
    

    // --- Leaderboard Functions ---
    function updateLeaderboard(tempScore) {
        console.log('Updating leaderboard with score:', tempScore);
        fetch('/update-leaderboard/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCSRFToken(),
            },
            body: `user_score=${tempScore}&csrfmiddlewaretoken=${getCSRFToken()}`,
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success'){
                console.log('New total score:', data.new_score, score);
                console.log('LOOTBOX TO REWARD', data.lootboxes_to_reward);
                if (data.lootboxes_to_reward > 0) {
                    showlootboxesAwarded(data.lootbox_id, data.lootboxes_to_reward);
                }
            } else {
                console.log("ERROR UPDATING LEADERBOARD: ", data, data.lootboxes_to_reward);
                console.error('error updating leaderboard');
            }
        })
        .catch(error => console.error('Error:', error));
    }

    function getLeaderboard() {
        fetch("/get-bingame-leaderboard/")
        .then(response => response.json())
        .then(data => {
            console.log("Leaderboard data:", data);
            if (data.error) {
                console.error("Error fetching leaderboard:", data.error);
                return;
            }
            // Sort data by points in descending order
            data.sort((a, b) => b.bingame_points - a.bingame_points);
            for (let i = 0; i < 10; i++) {
                const leaderboardItem = document.getElementById(`leaderboard-item-${i + 1}`);
                if (leaderboardItem) {
                    if (data[i]) {
                        console.log(data[i]);
                        leaderboardItem.textContent = `${data[i].username} - ${data[i].bingame_points} pts`;
                    } else {
                        leaderboardItem.textContent = "---";
                    }
                }
            }
        })
        .catch(error => console.error("Error fetching leaderboard:", error));
    }

    // --- Fetch New Items ---
    async function fetchNewRandomItems() {
        try {
            const response = await fetch('/fetch-random-items/');
            if (!response.ok) {
                throw new Error('Failed to fetch random items');
            }
            
            const data = await response.json();
            const items = data.items;
            console.log('New random items:', items);
            // Clear existing items
            itemsContainer.innerHTML = '';
            
            items.forEach(itemData => {
                const itemDiv = document.createElement('div');
                itemDiv.classList.add('items');
                itemDiv.setAttribute('data-dropped-bin-id', '');
                itemDiv.id = itemData.id;
                itemDiv.setAttribute('data-correct-bin-id', itemData.bin_id);
                
                const img = document.createElement('img');
              
                console.log("ITEM IMAGE: ", itemData.item_image)
                img.src = itemData.item_image;

                img.alt = itemData.item_name;
                const itemName = document.createElement('p');
                itemName.textContent = itemData.item_name;
                itemDiv.appendChild(itemName);
                itemDiv.appendChild(img);
                itemsContainer.appendChild(itemDiv);
            });
            
            rebindItemEventListeners();
        } catch (error) {
            console.error('Error fetching new random items:', error);
        }
    }

    // --- Lootbox Popup ---
    function showlootboxesAwarded(lootbox_id, quantity) {
        const lootboxPopup = document.createElement('div');
        lootboxPopup.id = 'lootbox-popup';
        
        const lootboxContent = document.createElement('div');
        lootboxContent.id = 'lootbox-content';
        lootboxPopup.appendChild(lootboxContent);
        
        fetch(`/get-lootbox-data/?lootbox_id=${lootbox_id}`)
        .then(response => response.json())
        .then(data => {

            const lootboxImage = document.createElement('img');
            lootboxImage.src = data.lootbox_image;
            lootboxImage.alt = data.lootbox_name;
            lootboxContent.appendChild(lootboxImage);
            
            const lootboxName = document.createElement('p');
            lootboxName.textContent = data.lootbox_name;
            lootboxContent.appendChild(lootboxName);
            
            const lootboxQuantity = document.createElement('p');
            lootboxQuantity.textContent = `Quantity: ${quantity}`;
            lootboxContent.appendChild(lootboxQuantity);
            
            const lootboxCloseBtn = document.createElement('button');
            lootboxCloseBtn.textContent = 'Close';
            lootboxCloseBtn.addEventListener('click', () => {
                lootboxPopup.remove();
            });
            lootboxContent.appendChild(lootboxCloseBtn);
            
            document.body.appendChild(lootboxPopup);
        })
        .catch(error => console.error("Error fetching lootbox data:", error));
    }

    // --- Initial Setup ---
    rebindItemEventListeners();
    bindDestinationListeners();
    getLeaderboard();
    document.getElementById('check-answer-tile').addEventListener('click', checkAnswers);
    document.getElementById('attempts-left').innerText = `Attempts left: ${maxAttempts - attempts}`;
    
    // Optional: clicking anywhere outside of an item/destination clears the selection.
    document.addEventListener('click', clearSelection);
});