from django.http import HttpResponseRedirect
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
import time

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_time = time.time()
            last_activity = request.session.get('last_activity', 0)
            
            # If session is expired, log out user
            if (current_time - last_activity) > settings.SESSION_EXPIRE_SECONDS:
                messages.warning(request, 'Your session has expired. Please log in again.')
                return HttpResponseRedirect(reverse('login'))
            
            request.session['last_activity'] = current_time

        return self.get_response(request)

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.MAINTENANCE_MODE and not request.user.is_staff:
            messages.warning(request, 'System is under maintenance. Please try again later.')
            return HttpResponseRedirect(reverse('maintenance'))
        return self.get_response(request)

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Security Headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()'
        
        # Only add HSTS header on HTTPS connections
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timer
        start_time = time.time()
        
        # Process request
        response = self.get_response(request)
        
        # Calculate request duration
        duration = time.time() - start_time
        
        # Log only if duration exceeds threshold (e.g., 1 second)
        if duration > 1:
            print(f"Slow request ({duration:.2f}s): {request.method} {request.path}")
        
        return response

class IPBlockingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(settings, 'BLOCKED_IPS') and request.META.get('REMOTE_ADDR') in settings.BLOCKED_IPS:
            messages.error(request, 'Access denied.')
            return HttpResponseRedirect(reverse('access_denied'))
        return self.get_response(request)