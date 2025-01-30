// Document Form Validation
document.addEventListener('DOMContentLoaded', function() {
    const documentForm = document.getElementById('documentForm');
    if (documentForm) {
        documentForm.addEventListener('submit', validateForm);
    }

    // Initialize date pickers
    const datePickers = document.querySelectorAll('input[type="date"]');
    datePickers.forEach(setupDatePicker);

    // Initialize preview functionality
    const previewButton = document.getElementById('previewButton');
    if (previewButton) {
        previewButton.addEventListener('click', showPreview);
    }
});

// Form Validation
function validateForm(event) {
    let isValid = true;
    const requiredFields = document.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            showError(field, 'This field is required');
        } else {
            clearError(field);
        }
    });

    // Additional validation for specific fields
    const titleField = document.getElementById('id_title');
    if (titleField && titleField.value.length > 255) {
        isValid = false;
        showError(titleField, 'Title must be less than 255 characters');
    }

    if (!isValid) {
        event.preventDefault();
    }
}

// Error Display
function showError(field, message) {
    clearError(field);
    field.classList.add('is-invalid');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

function clearError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Date Picker Setup
function setupDatePicker(dateInput) {
    // Prevent past dates if needed
    dateInput.min = new Date().toISOString().split('T')[0];
    
    dateInput.addEventListener('change', function() {
        validateDate(this);
    });
}

function validateDate(dateInput) {
    const selectedDate = new Date(dateInput.value);
    const today = new Date();
    
    if (selectedDate < today) {
        showError(dateInput, 'Date cannot be in the past');
        dateInput.value = '';
    } else {
        clearError(dateInput);
    }
}

// Preview Functionality
function showPreview(event) {
    event.preventDefault();
    
    const formData = new FormData(document.getElementById('documentForm'));
    const previewContainer = document.getElementById('previewContainer');
    
    // Update preview content
    previewContainer.innerHTML = generatePreviewHtml(formData);
    
    // Show preview modal
    const previewModal = new bootstrap.Modal(document.getElementById('previewModal'));
    previewModal.show();
}

function generatePreviewHtml(formData) {
    let html = `
        <div class="preview-document">
            <div class="document-header">
                <h1>${formData.get('title')}</h1>
                <div class="office-name">${formData.get('office_name')}</div>
                <div class="document-date">${formatDate(formData.get('date'))}</div>
            </div>
            <div class="receiver-info">
                <strong>To:</strong> ${formData.get('receiver')}
            </div>
            <div class="section">
                <h2>Description</h2>
                <div>${formData.get('description')}</div>
            </div>
            <div class="section">
                <h2>Summary</h2>
                <div>${formData.get('summary')}</div>
            </div>
            <div class="section">
                <h2>Object</h2>
                <div>${formData.get('object')}</div>
            </div>
        </div>
    `;
    return html;
}

// Utility Functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Document Status Updates
function updateStatus(documentId, status) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    fetch(`/document/${documentId}/status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error updating status: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while updating the status');
    });
}

// Print Functionality
function printDocument() {
    const printContents = document.querySelector('.preview-container').innerHTML;
    const originalContents = document.body.innerHTML;

    document.body.innerHTML = printContents;
    window.print();
    document.body.innerHTML = originalContents;
    
    // Reinitialize event listeners after restoring content
    document.addEventListener('DOMContentLoaded', function() {
        initializeEventListeners();
    });
}