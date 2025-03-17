function sharePost(postId) {
    const url = `${window.location.origin}${window.location.pathname}?post_id=${postId}`;
    navigator.clipboard.writeText(url).then(() => {
        alert('Link copied to clipboard!');
    });
}

function toggleComments(postId) {
    const commentsContainer = document.getElementById(`comments-${postId}`);
    const commentsChevron = document.getElementById(`post-comments-toggle-image`);
    commentsChevron.src = commentsContainer.style.display === 'none' ? chevronUp : chevronDown;
    commentsContainer.style.display = commentsContainer.style.display === 'none' ? 'block' : 'none';
}

function likePost(postId) {
    const likeButton = document.querySelector(`#like-button-${postId}`);
    likeButton.disabled = true;

    fetch(`/like/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const likeCountText = document.querySelector(`#like-count-${postId}`);
            likeCountText.textContent = data.likes;
            likeButton.src = data.liked ? likedButton : notLikedButton;
        } else {
            alert('Error updating like');
        }
        likeButton.disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        likeButton.disabled = false;
    });
}

function addComment(event, postId) {
    event.preventDefault();
    const form = event.target;
    const commentText = form.comment.value;

    fetch(`/add_comment/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content'),
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            'text': commentText
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const commentsContainer = document.getElementById(`comments-${postId}`);
            const newComment = document.createElement('div');
            newComment.classList.add('comment');
            newComment.innerHTML = `<p><strong>${data.user_email}</strong>: ${data.text}</p>`;
            commentsContainer.insertBefore(newComment, form.nextSibling);
            form.reset();
        } else {
            alert('Error adding comment');
        }
    })
    .catch(error => console.error('Error:', error));
}

function reportPost(postId) {
    const reportButton = document.querySelector(`#report-button-${postId}`);
    reportButton.disabled = true;

    fetch(`/report/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content'),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message || 'Post reported successfully.');
        } else {
            alert(data.message || 'You have already reported this post.');
        }
        reportButton.disabled = false;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error reporting post');
        reportButton.disabled = false;
    });
}