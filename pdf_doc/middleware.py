from datetime import timezone
from django.http import HttpResponseForbidden
from django.conf import settings
import re

class SecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile path regex patterns
        self.protected_paths = [
            re.compile(r'^/document/\d+/print/$'),
            re.compile(r'^/document/\d+/download/$'),
        ]

    def __call__(self, request):
        # Add security headers
        response = self.get_response(request)
        
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data:; font-src 'self' https://cdn.jsdelivr.net;"
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Check if path requires special protection
        path = request.path_info
        
        # Check for protected paths
        if any(pattern.match(path) for pattern in self.protected_paths):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Authentication required")
                
            # Additional checks for document access
            if 'document_id' in view_kwargs:
                from .models import PDFDocument
                try:
                    document = PDFDocument.objects.get(id=view_kwargs['document_id'])
                    if not self.can_access_document(request.user, document):
                        return HttpResponseForbidden("Access denied")
                except PDFDocument.DoesNotExist:
                    return HttpResponseForbidden("Document not found")

    def can_access_document(self, user, document):
        """
        Check if user can access the document.
        """
        # Staff can access all documents
        if user.is_staff:
            return True
            
        # Document creator can access their own documents
        if document.created_by == user:
            return True
            
        # Users can access accepted documents
        if document.status == 'accepted' and document.accepted_by is not None:
            return True
            
        return False

class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        if request.user.is_authenticated:
            # Update last activity timestamp
            request.user.profile.last_activity = timezone.now()
            request.user.profile.save()
        
        return response