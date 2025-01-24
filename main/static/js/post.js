// static/main/js/posts.js

// Like functionality
function likePost(postId) {
    fetch('/post/like/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: JSON.stringify({
            'post_id': postId
        })
    })
    .then(response => response.json())
    .then(data => {
        const likeButton = document.getElementById(`like-button-${postId}`);
        const likeCount = document.getElementById(`like-count-${postId}`);
        
        if (data.liked) {
            likeButton.classList.add('liked');
            likeButton.innerHTML = '<i class="bi bi-heart-fill"></i>';
        } else {
            likeButton.classList.remove('liked');
            likeButton.innerHTML = '<i class="bi bi-heart"></i>';
        }
        
        likeCount.textContent = data.like_count;
    })
    .catch(error => console.error('Error:', error));
}

// Share functionality
function sharePost(url, platform) {
    let shareWindow;
    
    switch(platform) {
        case 'facebook':
            shareWindow = window.open(
                `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
                'facebook-share',
                'width=600,height=400'
            );
            break;
            
        case 'twitter':
            shareWindow = window.open(
                `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}`,
                'twitter-share',
                'width=600,height=400'
            );
            break;
            
        case 'linkedin':
            shareWindow = window.open(
                `https://www.linkedin.com/shareArticle?mini=true&url=${encodeURIComponent(url)}`,
                'linkedin-share',
                'width=600,height=400'
            );
            break;
    }

    // Track share analytics
    fetch(`/post/share/?platform=${platform}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    });
}

// Add comment functionality
function addComment(postSlug) {
    const form = document.getElementById('comment-form');
    const formData = new FormData(form);

    fetch(`/post/${postSlug}/comment/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Add new comment to the list
            const commentsList = document.getElementById('comments-list');
            const newComment = createCommentElement(data);
            commentsList.insertBefore(newComment, commentsList.firstChild);
            
            // Clear form
            form.reset();
        } else {
            // Handle errors
            Object.keys(data.errors).forEach(key => {
                const error = data.errors[key];
                messages.error(error[0]);
            });
        }
    })
    .catch(error => console.error('Error:', error));
}

function createCommentElement(data) {
    const div = document.createElement('div');
    div.className = 'comment mb-3';
    div.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h6 class="card-subtitle mb-2 text-muted">${data.author}</h6>
                <p class="card-text">${data.content}</p>
                <small class="text-muted">${data.created_date}</small>
            </div>
        </div>
    `;
    return div;
}