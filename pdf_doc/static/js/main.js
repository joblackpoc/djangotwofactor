// Form Validation
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Auto-submit search form on select change
    const statusSelect = document.querySelector('select[name="status"]');
    if (statusSelect) {
        statusSelect.addEventListener('change', function() {
            this.closest('form').submit();
        });
    }

    // Date range validation
    const dateFrom = document.querySelector('input[name="date_from"]');
    const dateTo = document.querySelector('input[name="date_to"]');
    if (dateFrom && dateTo) {
        dateFrom.addEventListener('change', function() {
            dateTo.min = this.value;
        });
        dateTo.addEventListener('change', function() {
            dateFrom.max = this.value;
        });
    }

    // Print PDF button
    const printPdfBtn = document.querySelector('.print-pdf');
    if (printPdfBtn) {
        printPdfBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    }

    // Approval form validation
    const approvalForm = document.querySelector('#approvalForm');
    if (approvalForm) {
        approvalForm.addEventListener('submit', function(e) {
            const status = this.querySelector('select[name="status"]').value;
            const result = this.querySelector('textarea[name="result"]').value;

            if (status && !result.trim()) {
                e.preventDefault();
                alert('Please provide a result/comment for your decision.');
            }
        });
    }

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // File input preview
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileName = this.files[0]?.name;
            const label = this.nextElementSibling;
            label.textContent = fileName || 'Choose file';
        });
    }

    // Confirmation dialogs
    const confirmButtons = document.querySelectorAll('[data-confirm]');
    confirmButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });

    // Handle back button
    const backButtons = document.querySelectorAll('.btn-back');
    backButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.history.back();
        });
    });
});

// AJAX for real-time status updates
function updateDocumentStatus(documentId, status) {
    fetch(`/api/documents/${documentId}/status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
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
        alert('An error occurred while updating the status.');
    });
}

// Document preview functionality
function previewDocument(documentId) {
    const previewWindow = window.open('', '_blank');
    fetch(`/documents/${documentId}/preview/`)
        .then(response => response.text())
        .then(html => {
            previewWindow.document.write(html);
            previewWindow.document.close();
        })
        .catch(error => {
            console.error('Error:', error);
            previewWindow.close();
            alert('Error loading preview');
        });
}