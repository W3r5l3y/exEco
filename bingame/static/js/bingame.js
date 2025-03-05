document.addEventListener('DOMContentLoaded', () => {
    let newX = 0, newY = 0, startX = 0, startY = 0;
    let currentItem = null;
    let attempts = 0;
    let score = 0;
    const maxAttempts = 3;
    const itemsContainer = document.getElementById('items-container');

    function rebindItemEventListeners() {
        document.querySelectorAll('.items').forEach(item => {
            // Store initial position relative to items-container
            const containerRect = itemsContainer.getBoundingClientRect();
            const itemRect = item.getBoundingClientRect();

            item.dataset.originalLeft = itemRect.left - containerRect.left;
            item.dataset.originalTop = itemRect.top - containerRect.top;

            

            item.addEventListener('mousedown', mouseDown);
        });

        // Prevent image dragging inside items
        document.querySelectorAll('.items img').forEach(img => {
            img.ondragstart = (e) => e.preventDefault();
        });
    }

    function getCSRFToken() {
        const cookies = document.cookie.split("; ");
        for (let cookie of cookies) {
            const [name, value] = cookie.split("=");
            if (name === "csrftoken") return value;
        }
        return "";
    }

    /* --------------------------------------------------
    * Move items
    * -------------------------------------------------- */

    function resetItemPosition(item) {
        item.style.removeProperty('left');
        item.style.removeProperty('top');
        item.style.removeProperty('transform');
        item.style.removeProperty('position'); 
        item.removeAttribute('data-dropped-bin-id'); // If needed
    }

    function mouseDown(e) {
        currentItem = e.target.closest('.items');
        if (!currentItem) return;

        startX = e.clientX;
        startY = e.clientY;

        document.addEventListener('mousemove', mouseMove);
        document.addEventListener('mouseup', mouseUp);
    }

    function mouseMove(e) {
        if (!currentItem) return;

        newX = startX - e.clientX;
        newY = startY - e.clientY;

        startX = e.clientX;
        startY = e.clientY;

        currentItem.style.position = "absolute"; // Ensure absolute positioning
        currentItem.style.left = `${currentItem.offsetLeft - newX}px`;
        currentItem.style.top = `${currentItem.offsetTop - newY}px`;
    }

    function mouseUp(e) {
        document.removeEventListener('mousemove', mouseMove);
        if (!currentItem) return;
    
        currentItem.removeAttribute('data-dropped-bin-id'); // Clear previous bin ID
    
        const bins = document.querySelectorAll('.bin');
        let droppedInBin = false;
    
        bins.forEach(bin => {
            const binRect = bin.getBoundingClientRect();
            const itemRect = currentItem.getBoundingClientRect();
    
            if (
                itemRect.right > binRect.left &&
                itemRect.left < binRect.right &&
                itemRect.bottom > binRect.top &&
                itemRect.top < binRect.bottom
            ) {
                droppedInBin = true;
                currentItem.style.left = `${binRect.left + (binRect.width - itemRect.width) / 2 - itemsContainer.getBoundingClientRect().left}px`;
                currentItem.style.top = `${binRect.top + (binRect.height - itemRect.height) / 2 - itemsContainer.getBoundingClientRect().top}px`;
    
                const binId = bin.getAttribute('data-bin-id');
                if (binId) {
                    currentItem.setAttribute('data-dropped-bin-id', binId);
                    console.log(`Item dropped in bin with ID: ${binId}`);
                }
            }
        });
    
        if (!droppedInBin) {
            resetItemPosition(currentItem);
        }
    
        currentItem = null;
    }
    


    /* --------------------------------------------------
    * Submit and validate
    * -------------------------------------------------- */

    document.getElementById('check-answer-tile').addEventListener('click', checkAnswers);

    function checkAnswers() {
        const items = document.querySelectorAll('.items');
        const totalItems = items.length; // Ensure this is set
        let allPlaced = true;
    
        items.forEach(item => {
            if (!item.getAttribute('data-dropped-bin-id')) {
                allPlaced = false;
                item.style.border = '2px dashed red';
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
                item.classList.add('correct'); // Ensure correct class is applied
                item.removeEventListener('mousedown', mouseDown);
            } else {
                item.classList.remove('correct'); // Reset incorrect ones
                resetItemPosition(item);
                item.style.border = '2px solid rgb(240, 152, 149)';
                item.removeAttribute('data-dropped-bin-id');
            }
        });

    
        // Count correct items properly
        correctCount = document.querySelectorAll('.items.correct').length;
    
        if (correctCount === totalItems || attempts >= maxAttempts) {
            let tempScore = calculateScore();
            endGame(tempScore);
        }
    
        // Ensure attempts-left updates correctly
        const attemptsLeftElem = document.getElementById('attempts-left');
        if (attemptsLeftElem) {
            attemptsLeftElem.innerText = `Attempts left: ${maxAttempts - attempts}`;
        }
    }    

    function calculateScore() {
        if (attempts >= maxAttempts) {
            return 0; // Ensure no points if max attempts are used up
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
    
        // Remove all items
        itemsContainer.innerHTML = '';
    
        // Create result message
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
    
        checkAnswerBtn.innerText = 'Next Round';
        checkAnswerBtn.removeEventListener('click', checkAnswers);
        checkAnswerBtn.addEventListener('click', resetGame);
    
        if (attemptsLeftElem) {
            attemptsLeftElem.style.display = 'none'; // Hide attempts left
        }
    }    

    function resetGame() {
        attempts = 0;
        score = 0;
    
        const itemsContainer = document.getElementById('items-container');
        const checkAnswerBtn = document.getElementById('check-answer-tile');
        const attemptsLeftElem = document.getElementById('attempts-left');
    
        // Reset container styling and remove game result message
        itemsContainer.style.backgroundColor = '';
        itemsContainer.innerHTML = '';
    
        getLeaderboard();
        fetchNewRandomItems();
    
        checkAnswerBtn.innerText = 'Check Answers';
        checkAnswerBtn.removeEventListener('click', resetGame);
        checkAnswerBtn.addEventListener('click', checkAnswers);
    
        if (attemptsLeftElem) {
            attemptsLeftElem.style.display = 'block'; // Show attempts left
            attemptsLeftElem.innerText = `Attempts left: ${maxAttempts - attempts}`;
        }
    }
    
    
    
    

    /* --------------------------------------------------
    * Leaderboard
    * -------------------------------------------------- */

    function updateLeaderboard(tempScore){
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
            return response.json();
        })
        .then(data => {
            if (data.status === 'success'){
                console.log('New total score:', data.new_score, score);
                
                // Show lootboxes awarded
                if (data.lootboxes_awarded > 0) {
                    showlootboxesAwarded(data.lootboxes_awarded);
                }
            } else{
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
    
                // Ensure data is sorted by user_score in descending order
                data.sort((a, b) => b.bingame_points - a.bingame_points);
    
                // Loop through the leaderboard items and update them
                for (let i = 0; i < 10; i++) {
                    const leaderboardItem = document.getElementById(`leaderboard-item-${i + 1}`);
                    
                    if (leaderboardItem) {
                        if (data[i]) {
                            console.log(data[i]);
                            leaderboardItem.textContent = `${data[i].username} - ${data[i].bingame_points} pts`;
                        } else {
                            leaderboardItem.textContent = "---"; // Placeholder if no data available
                        }
                    }
                }
            })
            .catch(error => console.error("Error fetching leaderboard:", error));
    }

    /* --------------------------------------------------
    * Fetch new items
    * -------------------------------------------------- */
    async function fetchNewRandomItems() {
        try {
            const response = await fetch('/fetch_random_items/');
            if (!response.ok) {
                throw new Error('Failed to fetch random items');
            }
            
            const data = await response.json();
            const items = data.items; 
            console.log('New random items:', items);
    
            //Remove the items
            const itemsContainer = document.getElementById('items-container');
            itemsContainer.innerHTML = '';
    
            //Get the new item elements
            items.forEach(itemData => {
                const itemDiv = document.createElement('div');
                itemDiv.classList.add('items');
                itemDiv.setAttribute('data-dropped-bin-id', '');
                itemDiv.id = itemData.id;
                itemDiv.setAttribute('data-correct-bin-id', itemData.bin_id);
    
                const img = document.createElement('img');
                console.log("ITEM IMAGE: ", itemData.item_image)
                img.src = `/static/${itemData.item_image}`;
                img.alt = itemData.item_name;
                const itemName = document.createElement('p');
                itemName.textContent = itemData.item_name;
                itemDiv.appendChild(itemName);
                itemDiv.appendChild(img);
                itemsContainer.appendChild(itemDiv);
            });
    
            //Put listeners back onto the new items
            rebindItemEventListeners();
    
        } catch (error) {
            console.error('Error fetching new random items:', error);
        }
    }

    // --------------------------------------------------
    // Lootbox popup
    // --------------------------------------------------

    function showlootboxesAwarded(lootboxesAwarded) {
        const lootboxPopup = document.getElementById('lootbox-popup');
        lootboxPopup.style.display = 'block';
    
        const lootboxCountElem = document.getElementById('lootbox-count');
        lootboxCountElem.textContent = `+${lootboxesAwarded} lootboxes!`;
    
        setTimeout(() => {
            lootboxPopup.style.display = 'none';
        }, 3000);
    }
    // --------------------------------------------------
    // Initial setup
    // --------------------------------------------------
    rebindItemEventListeners();
    getLeaderboard();
    document.getElementById('attempts-left').innerText = `Attempts left: ${maxAttempts - attempts}`;
});
