function sharePost(postId) {
        const url = `${window.location.origin}${window.location.pathname}?post_id=${postId}`;
        navigator.clipboard.writeText(url).then(() => {
            alert('Link copied to clipboard!');
        });
    }

    function toggleComments(postId) {
        const commentsContainer = document.getElementById(`comments-${postId}`);
        commentsContainer.style.display = commentsContainer.style.display === 'none' ? 'block' : 'none';
    }

    function likePost(postId) {
        fetch(`/like/${postId}/`.replace('0', postId), {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').getAttribute('content'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
            const likeCountText = document.querySelector(`#like-count-${postId}`);
            likeCountText.textContent = data.likes;
            const likeButton = document.querySelector(`#like-button-${postId}`);
            likeButton.src = data.liked ? likedButton : likeButton;
        })
        .catch(error => console.error('Error:', error));
    }