
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