// static/main/js/comments.js

function likeComment(commentId) {
    fetch(`/comment/${commentId}/like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update like button appearance
            const likeButton = document.querySelector(`#comment-like-${data.comment_id}`);
            const likeCount = document.querySelector(`#comment-likes-count-${data.comment_id}`);
            
            if (data.liked) {
                likeButton.classList.add('text-danger');
                likeButton.innerHTML = '<i class="bi bi-heart-fill"></i>';
            } else {
                likeButton.classList.remove('text-danger');
                likeButton.innerHTML = '<i class="bi bi-heart"></i>';
            }
            
            // Update like count
            likeCount.textContent = data.likes_count;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while processing your request.');
    });
}

// Add this to your static/main/js/comments.js file

function deleteComment(commentId) {
    if (confirm('Are you sure you want to delete this comment?')) {
        fetch(`/comment/${commentId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (response.ok) {
                return response.json();
            }
            throw new Error('Network response was not ok');
        })
        .then(data => {
            if (data.status === 'success') {
                // Remove the comment from the DOM
                const commentElement = document.getElementById(`comment-${commentId}`);
                commentElement.remove();
                
                // Optional: Update comment count if you're displaying it
                const commentCount = document.getElementById('comment-count');
                if (commentCount) {
                    const currentCount = parseInt(commentCount.textContent);
                    commentCount.textContent = currentCount - 1;
                }

                // Optional: Show success message
                showAlert('success', 'Comment deleted successfully');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('error', 'Failed to delete comment. Please try again.');
        });
    }
}

// Helper function to show alerts
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const alertsContainer = document.getElementById('alerts-container');
    if (alertsContainer) {
        alertsContainer.appendChild(alertDiv);
        
        // Auto-remove alert after 3 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }
}

// static/main/js/comments.js

function toggleReplyForm(commentId) {
    const form = document.getElementById(`reply-form-${commentId}`);
    if (form) {
        form.style.display = form.style.display === 'none' ? 'block' : 'none';
        if (form.style.display === 'block') {
            form.querySelector('textarea').focus();
        }
    }
}

// Handle reply form submission
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.reply-form form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Add new reply to the list
                    const repliesContainer = this.closest('.comment')
                        .querySelector('.replies');
                    const replyHtml = createReplyHTML(data);
                    repliesContainer.insertAdjacentHTML('beforeend', replyHtml);
                    
                    // Clear and hide form
                    this.reset();
                    this.closest('.reply-form').style.display = 'none';
                    
                    // Show success message
                    showAlert('success', 'Reply added successfully!');
                } else {
                    showAlert('error', 'Error adding reply. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('error', 'An error occurred. Please try again.');
            });
        });
    });
});

function createReplyHTML(data) {
    return `
        <div class="reply mb-2" id="reply-${data.reply_id}">
            <div class="card">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <h6 class="card-subtitle mb-2 text-muted">${data.author}</h6>
                        <small class="text-muted">${data.created_date}</small>
                    </div>
                    <p class="card-text">${data.content}</p>
                    <button class="btn btn-sm btn-link text-danger p-0" 
                            onclick="deleteReply(${data.reply_id})">
                        <i class="bi bi-trash"></i> Delete
                    </button>
                </div>
            </div>
        </div>
    `;
}

function deleteReply(replyId) {
    if (confirm('Are you sure you want to delete this reply?')) {
        fetch(`/reply/${replyId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById(`reply-${replyId}`).remove();
                showAlert('success', 'Reply deleted successfully!');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('error', 'Error deleting reply. Please try again.');
        });
    }
}

function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const alertsContainer = document.getElementById('alerts-container');
    if (alertsContainer) {
        alertsContainer.appendChild(alertDiv);
        setTimeout(() => alertDiv.remove(), 3000);
    }
}