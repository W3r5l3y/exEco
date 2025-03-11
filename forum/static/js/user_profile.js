function goToPost(postId) {
    window.location.href = `${window.location.origin}/forum/?post_id=${postId}`;
}



document.querySelectorAll('.own-post').forEach(postElement => {
        var originalDescriptionText = '';
        let state = 'none';

        const editInput = postElement.querySelector('.own-post-description');
        const leftImage = postElement.querySelector('.left-image');
        const rightImage = postElement.querySelector('.right-image');
        const postImage = postElement.querySelector('.own-post-image');



        leftImage.addEventListener('click', function () {
            if (state === 'none') {

                originalDescriptionText = editInput.value;
                leftImage.src = crossButton;
                rightImage.src = checkButton;
                editInput.style.color = "red";
                editInput.value = 'Confirm Delete?';
                state = 'delete';
            } else if (state === 'edit') {

                postImage.style.opacity = 1;
                editInput.value = originalDescriptionText;
                editInput.classList.toggle('own-post-description-editing');
                editInput.disabled = !editInput.disabled;

                leftImage.src = deleteButton;
                rightImage.src = editButton;
                state = 'none';
            } else if (state === 'delete') {

                editInput.value = originalDescriptionText;

                leftImage.src = deleteButton;
                rightImage.src = editButton;
                editInput.style.color = "white";
                state = 'none';
            }
        });

       rightImage.addEventListener('click', function () {
            if (state === 'none') {
                postImage.style.opacity = .5;
                originalDescriptionText = editInput.value;
                editInput.classList.toggle('own-post-description-editing');
                editInput.disabled = !editInput.disabled;
                leftImage.src = crossButton;
                rightImage.src = checkButton;
                state = 'edit';
            } else if (state === 'edit') {

                postImage.style.opacity= 1;
                editInput.disabled = !editInput.disabled;
                editInput.classList.toggle('own-post-description-editing');
                leftImage.src = deleteButton;
                rightImage.src = editButton;
                state = 'none';
            } else if (state === 'delete') {

                leftImage.src = deleteButton;
                rightImage.src = editButton;
                editInput.style.color = "white";
                state = 'none';
            }
        });

    });


function toggleDeleteState(ownPostElement, isConfirming) {
        const editInput = ownPostElement.querySelector('.own-post-description');
        const leftImage = ownPostElement.querySelector('.left-image');
        const rightImage = ownPostElement.querySelector('.right-image');
        const originalText = editInput.dataset.originalText || editInput.value;

        if (isConfirming) {
            editInput.dataset.originalText = originalText;
            editInput.value = "Confirm deletion?";
            editInput.style.color = "red";
            leftImage.src = crossButton;
        } else {
            editInput.value = originalText;
            editInput.style.color = "";
            leftImage.src = deleteButton;
        }
    }


function toggleEditState(postElement, ) {
    const editInput = postElement.querySelector('.own-post-description');
    const rightButton = postElement.querySelector('.right-image');
    const leftButton = postElement.querySelector('.left-image');
    console.log('hehe');
    if (isEditing) {
        editInput.disabled = false;
        editInput.classList.add('own-post-description-editing');
        rightButton.src = checkButton;
        leftButton.src = crossButton;
    } else {
        editInput.disabled = true;
        editInput.classList.remove('own-post-description-editing');
        rightButton.src = editButton;
        leftButton.src = deleteButton;
    }
}

