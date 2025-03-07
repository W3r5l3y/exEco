function sharePost(postId) {
        const url = `${window.location.origin}${window.location.pathname}?post_id=${postId}`;
        navigator.clipboard.writeText(url).then(() => {
            alert('Link copied to clipboard!');
        });
    }

    function toggleComments(postId) {
        const commentsContainer = document.getElementById(`comments-${postId}`);
        const commentsChevron = document.getElementById(`post-comments-toggle-image`)
        commentsChevron.src = commentsContainer.style.display === 'none' ? chevronUp : chevronDown;
        commentsContainer.style.display = commentsContainer.style.display === 'none' ? 'block' : 'none';
    }

    function likePost(postId) {
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
            const likeCountText = document.querySelector(`#like-count-${postId}`);
            likeCountText.textContent = data.likes;
            const likeButton = document.querySelector(`#like-button-${postId}`);
            const heartButton = document.querySelector(`#like-heart-${postId}`);
            likeCountText.style.color = data.liked ? getComputedStyle(document.documentElement).getPropertyValue('--accessories_colour').trim() : "white";
            heartButton.src = data.liked ? activeHeart : nonActiveHeart;
            likeButton.src = data.liked ? likedButton : notLikedButton;
        })
        .catch(error => console.error('Error:', error));
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