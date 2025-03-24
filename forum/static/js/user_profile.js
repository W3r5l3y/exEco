// Have event listeners for each individual post
document.querySelectorAll('.own-post').forEach(postElement => {
    let originalDescriptionText = '';
    let state = 'none';

    const editInput = postElement.querySelector('.own-post-description');
    const leftImage = postElement.querySelector('.left-image');
    const rightImage = postElement.querySelector('.right-image');
    const postImage = postElement.querySelector('.own-post-image');
    const postId = postElement.dataset.postId;
    /**
     * Detect left image click.
     * Depending on the state the post is currently in (none/editing/deleting),
     * a different outcome/design will occur
     */
    leftImage.addEventListener('click', function () {
        if (state === 'none') {
            //Send image into delete state and design
            originalDescriptionText = editInput.value;
            leftImage.src = crossButton;
            rightImage.src = checkButton;
            editInput.style.color = "red";
            editInput.value = 'Confirm Delete?';
            state = 'delete';
        } else if (state === 'edit') {
            //Send image into default state
            cancelEditMode();
        } else if (state === 'delete') {
            //Send image into default state
            cancelDeleteMode();
        }
    });

    /**
     * Detect right image click.
     * Depending on the state the post is currently in (none/editing/deleting),
     * a different outcome/design will occur
     */
    rightImage.addEventListener('click', function () {
        if (state === 'none') {
            //Send image into edit state
            enterEditMode();
        } else if (state === 'edit') {
            //Send image into default state and submit the edit changes
            submitEdit();
        } else if (state === 'delete') {
            //Delete post
            submitDelete();
        }
    });

    /**
     * This function alters the state into the edit mode and
     * temporarily edits the design of the post in order to creat
     * visual feedback that the post is being edited.
     */
    function enterEditMode() {
        postImage.style.opacity = 0.5;
        originalDescriptionText = editInput.value;
        editInput.classList.add('own-post-description-editing');
        editInput.disabled = false;
        leftImage.src = crossButton;
        rightImage.src = checkButton;
        state = 'edit';
    }

    /**
     * This function alters the state into the default mode and
     * returns the design and description text back to how it was
     * prior to the edit state.
     */
    function cancelEditMode() {
        postImage.style.opacity = 1;
        //Restoring description text
        editInput.value = originalDescriptionText;
        editInput.classList.remove('own-post-description-editing');
        editInput.disabled = true;
        leftImage.src = deleteButton;
        rightImage.src = editButton;
        state = 'none';
    }

    /**
     * This function alters the state into the delete mode and
     * changes the design of the buttons to show this.
     */
    function cancelDeleteMode() {
        editInput.value = originalDescriptionText;
        editInput.style.color = "white";
        leftImage.src = deleteButton;
        rightImage.src = editButton;
        state = 'none';
    }

    /**
     * This function occurs once an edit is confirmed.
     * Firstly checking for errors with retrieving the post or CSRFToken,
     * it submits an edit by sending a POST request to the right url.
     */
    function submitEdit() {
        const postElement = editInput.closest('.own-post');
        if (!postElement) {
            console.error("Error: Could not find post container.");
            return;
        }
    
        const postId = postElement.dataset.postId;
        const csrfToken = getCSRFToken();
        //Checking for errors with post or CSRF retrieval
        if (!csrfToken || !postId) {
            console.error("CSRF token or Post ID not found!", { csrfToken, postId });
            return;
        }
    
        fetch(`/edit_post/${postId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,  // Using the CSRF token from cookies
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                description: editInput.value
            })
        })
        .then(response => response.json())
        .then(data => {
            //User feedback
            if (data.success) {
                alert("Post edited successfully");
                location.reload();
            } else {
                alert("Failed to edit post");
            }
        })
        .catch(error => console.error("Error:", error));
    }      

    /**
     * This function occurs once deletion is confirmed.
     * Firstly checking for errors with retrieving the post or CSRFToken,
     * it confirms deletion by sending a POST request to the right url.
     */
    function submitDelete() {
        const postElement = leftImage.closest('.own-post'); 
        if (!postElement) {
            console.error("Error: Could not find post container.");
            return;
        }
    
        const postId = postElement.dataset.postId;
        const csrfToken = getCSRFToken();

        //Checking for errors with post or CSRF retrieval
        if (!csrfToken || !postId) {
            console.error("CSRF token or Post ID not found!", { csrfToken, postId });
            return;
        }
    
        fetch(`/delete_post/${postId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,  // Using CSRF token from cookies
                "Content-Type": "application/json"
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            //User feedback
            if (data.success) {
                postElement.remove();
                alert("Post deleted successfully");
            } else {
                console.error("Failed to delete post.");
            }
        })
        .catch(error => console.error("Delete request failed:", error));
    }

    /**
     * This function attempts to retrieve the CSRFToken from the document cookies.
     *
     * @returns {*|string} the CSRF token
     */
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
        return cookieValue || "";
    } 
});
