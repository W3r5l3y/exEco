/*
DRAG AND DROP FUNCTIONALITY - Item
*/
let newX = 0, newY = 0, startX = 0, startY = 0;
//const item = document.querySelector('.items');
let currentItem = null;

//Gets all the items in the items class and adds an event listener to each
document.querySelectorAll('.items').forEach(item => {
    item.addEventListener('mousedown', mouseDown);
});

// Prevent image dragging inside items
document.querySelectorAll('.items img').forEach(img => {
    img.ondragstart = (e) => e.preventDefault();
});

// When the user clicks down
function mouseDown(e){
    // Select the item being clicked
    currentItem = e.target.closest('.items');
    // If clicking outside item area
    if (!currentItem) return;
    startX = e.clientX
    startY = e.clientY

    document.addEventListener('mousemove', mouseMove); 
    document.addEventListener('mouseup', mouseUp);

}

// When the user moves the mouse
function mouseMove(e){
    // Only move if selected
    if (!currentItem) return;
    newX = startX - e.clientX;
    newY = startY - e.clientY;

    startX = e.clientX;
    startY = e.clientY;

    currentItem.style.top = (currentItem.offsetTop - newY) + 'px';
    currentItem.style.left = (currentItem.offsetLeft - newX) + 'px';
    
}

// When the user releases the mouse
function mouseUp(e){
    document.removeEventListener('mousemove', mouseMove);

    if (!currentItem) return; //Item on a valid bin
    
    const bins = document.querySelectorAll('.bin');
    let droppedInBin = false;

    bins.forEach(bin => {
        const binRect = bin.getBoundingClientRect();
        const itemRect = currentItem.getBoundingClientRect();

        if (
            itemRect.left > binRect.left &&
            itemRect.right < binRect.right &&
            itemRect.top > binRect.top &&
            itemRect.bottom < binRect.bottom
        ) {
            droppedInBin = true;

            //Place bin in center on bin (change later so look nice but just for logic cause it enough to test)
            currentItem.style.left = `${binRect.left + (binRect.width - itemRect.width) / 2}px`;
            currentItem.style.top = `${binRect.top + (binRect.height - itemRect.height) / 2}px`;

            //mouseUpped in bin
            const binId = bin.getAttribute('data-bin-id');
            console.log(binId);
            if (binId) {
                currentItem.setAttribute('data-dropped-bin-id', binId);
                console.log(`Item dropped in bin with ID: ${binId}`);
            } else {
                console.log(' Bin ID not found!');
            }
            currentItem.setAttribute('data-dropped-bin-id', binId);
        }
    });
    //Reset if not on bin
    if (!droppedInBin) {
        currentItem.style.left = '50%';
        currentItem.style.top = '40%';
        currentItem.removeAttribute('data-dropped-bin-id');
    }

    currentItem = null; 
}


/*
CHECK ANSWER FUNCTIONALITY
*/
var attempts = 0;
var maxAttempts = 3
var totalItems = document.querySelectorAll('.items').length;
let score = 0;

document.getElementById('check-answer-tile').addEventListener('click', checkAnswers);
//The check answer function
function checkAnswers() {
    const items = document.querySelectorAll('.items');
    let allPlaced = true;
    let correctCount = 0;

    //Ensure all items are placed
    items.forEach(item => {
        if (!item.getAttribute('data-dropped-bin-id')) {
            allPlaced = false;
            item.style.border = '2px dashed red';
        }
    });
    //If not all placed, ask user to place the ones not yet placed
    if (!allPlaced) {
        alert('Please place all items in the correct bins');
        return;
    }

    attempts++;

    //Check for each item if its on the correct bin, use the correct bin id from django and the dropped from handleDrop()
    items.forEach(item => {
        const correctBinId = item.getAttribute('data-correct-bin-id');
        const droppedBinId = item.getAttribute('data-dropped-bin-id');
        item.style.border = 'none';
        console.log(`Correct ID: ${correctBinId}, Dropped ID: ${droppedBinId}`);
        if (!droppedBinId) {
            item.style.border = '2px dashed red';
        }
        else if(correctBinId === droppedBinId) {
            correctCount++;
            item.classList.add('correct');
            item.style.border = '2px solid green';
        } else {
            item.style.left = '50%';
            item.style.top = '40%';
            item.removeAttribute('data-dropped-bin-id');
            item.style.border = '2px solid red';
        }
    })

    // Count correct items
    correctCount = document.querySelectorAll('.items.correct').length;

    if (correctCount === totalItems){
        document.getElementById('attempts-left').innerText = `Attempts left: ${maxAttempts - attempts}`;
        var tempScore = calculateScore()
        endGame(tempScore);
    } else if (attempts >= maxAttempts){
        var tempScore = calculateScore()
        endGame(tempScore);
    }
}

function calculateScore(){
    let points = (maxAttempts - attempts + 1 ) * 2; //max = 3: if attempts = {1,2,3} points then = {6, 4, 2}
    score += points;
    return score
}

function endGame(tempScore){
    updateLeaderboard(tempScore)
    alert('Game over! Score: ' + score + ' ' + tempScore);
    resetGame();
}


/*
LEADERBOARD FUNCTIONALITY
*/
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
        } else{
            console.error('error updating leaderboard');
        }
    })
    .catch(error => console.error('Error:', error));
}

// Function to get CSRF token from cookies
function getCSRFToken() {
    const cookies = document.cookie.split("; ");
    for (let cookie of cookies) {
        const [name, value] = cookie.split("=");
        if (name === "csrftoken") return value;
    }
    return "";
}

//Gets the leaderboard to be displayed
function getLeaderboard() {
    fetch("/get-leaderboard/")
        .then(response => response.json())
        .then(data => {
            console.log("Leaderboard data:", data);
            if (data.error) {
                console.error("Error fetching leaderboard:", data.error);
                return;
            }

            // Ensure data is sorted by user_score in descending order
            data.sort((a, b) => b.user_score - a.user_score);

            // Loop through the leaderboard items and update them
            for (let i = 0; i < 10; i++) {
                const leaderboardItem = document.getElementById(`leaderboard-item-${i + 1}`);
                
                if (leaderboardItem) {
                    if (data[i]) {
                        console.log(data[i]);
                        leaderboardItem.textContent = `${data[i].user_id} - ${data[i].user_score} pts`;
                    } else {
                        leaderboardItem.textContent = "---"; // Placeholder if no data available
                    }
                }
            }
        })
        .catch(error => console.error("Error fetching leaderboard:", error));
}

/*
RESET FUNCTIONALITY
*/
function resetGame(){
    attempts = 0;
    score = 0;
    document.querySelectorAll('.items').forEach(item => {
        item.style.left = '50%';
        item.style.top = '40%';
        item.removeAttribute('data-dropped-bin-id');
        item.classList.remove('correct');
        item.style.border = 'none';
    });
    getLeaderboard();
    //Redirect to game_view in views.py
    fetchNewRandomItems();
}


async function fetchNewRandomItems() {
    try {
        const response = await fetch('/fetch_random_items/');
        if (!response.ok) {
            throw new Error('Failed to fetch random items');
        }
        
        const data = await response.json();
        const items = data.items; 

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
            img.src = itemData.item_image_url;
            img.alt = itemData.item_name;

            itemDiv.appendChild(img);
            itemsContainer.appendChild(itemDiv);
        });

        //Put listeners back onto the new items
        rebindItemEventListeners();

    } catch (error) {
        console.error('Error fetching new random items:', error);
    }
}



getLeaderboard(); // Update leaderboard on page load
