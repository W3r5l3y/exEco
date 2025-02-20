
let newX = 0, newY = 0, startX = 0, startY = 0;
//const item = document.querySelector('.items');
let currentItem = null;

/*
DataTransferItemList.forEach(item => {
    item.addEventListener('mousedown', mouseDown);
});
*/
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
    currentItem=null;
}