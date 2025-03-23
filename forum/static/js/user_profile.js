document.querySelectorAll('.own-post').forEach(postElement => {
    // Global variables
    let originalDescriptionText = '';
    let state = 'none';

    // Global constants
    const editInput = postElement.querySelector('.own-post-description');
    const leftImage = postElement.querySelector('.left-image');
    const rightImage = postElement.querySelector('.right-image');
    const postImage = postElement.querySelector('.own-post-image');
    const postId = postElement.dataset.postId;

    // Add event listeners to the left and right images
    leftImage.addEventListener('click', function () {
        if (state === 'none') {
            originalDescriptionText = editInput.value;
            leftImage.src = crossButton;
            rightImage.src = checkButton;
            editInput.style.color = "red";
            editInput.value = 'Confirm Delete?';
            state = 'delete';
        } else if (state === 'edit') {
            cancelEditMode();
        } else if (state === 'delete') {
            cancelDeleteMode();
        }
    });
    rightImage.addEventListener('click', function () {
        if (state === 'none') {
            enterEditMode();
        } else if (state === 'edit') {
            submitEdit();
        } else if (state === 'delete') {
            submitDelete();
        }
    });

    // Function to enter edit mode
    function enterEditMode() {
        postImage.style.opacity = 0.5;
        originalDescriptionText = editInput.value;
        editInput.classList.add('own-post-description-editing');
        editInput.disabled = false;
        leftImage.src = crossButton;
        rightImage.src = checkButton;
        state = 'edit';
    }

    // Function to cancel edit mode
    function cancelEditMode() {
        postImage.style.opacity = 1;
        editInput.value = originalDescriptionText;
        editInput.classList.remove('own-post-description-editing');
        editInput.disabled = true;
        leftImage.src = deleteButton;
        rightImage.src = editButton;
        state = 'none';
    }

    // Function to cancel delete mode
    function cancelDeleteMode() {
        editInput.value = originalDescriptionText;
        editInput.style.color = "white";
        leftImage.src = deleteButton;
        rightImage.src = editButton;
        state = 'none';
    }

    // Function to submit the edited post
    function submitEdit() {
        const postElement = editInput.closest('.own-post');
        if (!postElement) {
            console.error("Error: Could not find post container.");
            return;
        }
        
        // Get the post ID and CSRF token
        const postId = postElement.dataset.postId;
        const csrfToken = getCSRFToken();
    
        if (!csrfToken || !postId) {
            console.error("CSRF token or Post ID not found!", { csrfToken, postId });
            return;
        }
    
        // Send a POST request to the server to edit the post
        fetch(`/edit_post/${postId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                description: editInput.value
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Post edited successfully");
                location.reload();
            } else {
                alert("Failed to edit post");
            }
        })
        .catch(error => console.error("Error:", error));
    }      

    // Function to delete the post
    function submitDelete() {
        const postElement = leftImage.closest('.own-post'); 
        if (!postElement) {
            console.error("Error: Could not find post container.");
            return;
        }
    
        // Get the post ID and CSRF token
        const postId = postElement.dataset.postId;
        const csrfToken = getCSRFToken();
    
        if (!csrfToken || !postId) {
            console.error("CSRF token or Post ID not found!", { csrfToken, postId });
            return;
        }
    
        // Send a POST request to the server to delete the post
        fetch(`/delete_post/${postId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                postElement.remove();
                alert("Post deleted successfully");
            } else {
                console.error("Failed to delete post.");
            }
        })
        .catch(error => console.error("Delete request failed:", error));
    }        

    // Function to get the CSRF token
    function getCSRFToken() {
        const cookieValue = document.cookie
            .split("; ")
            .find(row => row.startsWith("csrftoken="))
            ?.split("=")[1];
        return cookieValue || "";
    } 
});
