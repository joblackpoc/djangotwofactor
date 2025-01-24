import os
import uuid
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible

@deconstructible
class PDFFileStorage(FileSystemStorage):
    """
    Custom storage backend for PDF files with unique naming
    """
    def get_available_name(self, name, max_length=None):
        """
        Generate a unique filename to prevent overwriting
        """
        # Split the filename and extension
        name_parts = os.path.splitext(name)
        
        # Generate a unique identifier
        unique_id = uuid.uuid4().hex[:8]
        
        # Construct new filename
        new_filename = f"{name_parts[0]}_{unique_id}{name_parts[1]}"
        
        # Ensure the full path length is within max_length
        if max_length and len(new_filename) > max_length:
            # Truncate the base filename to make room for the unique identifier
            base_name_max_length = max_length - len(unique_id) - len(name_parts[1]) - 2
            base_name = name_parts[0][:base_name_max_length]
            new_filename = f"{base_name}_{unique_id}{name_parts[1]}"
        
        return new_filename

    def _save(self, name, content):
        """
        Additional save logic if needed
        """
        # Validate file type
        self._validate_file_type(content)
        
        return super()._save(name, content)

    def _validate_file_type(self, content):
        """
        Validate that the uploaded file is a PDF
        """
        # Check file extension
        allowed_extensions = ['.pdf']
        file_ext = os.path.splitext(content.name)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise ValueError(f"File type {file_ext} is not allowed. Only PDFs are permitted.")
        
        # Optional: Additional PDF validation
        try:
            # Check PDF header
            header = content.read(4)
            content.seek(0)  # Reset file pointer
            
            # PDF files start with %PDF
            if header != b'%PDF':
                raise ValueError("Invalid PDF file")
        except Exception as e:
            raise ValueError("Unable to validate PDF file") from e