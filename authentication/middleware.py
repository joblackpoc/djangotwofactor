from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
from django.conf import settings
from datetime import datetime
class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity = request.session.get('last_activity')
            if last_activity:
                # Convert timestamp to datetime object in the current timezone
                last_activity_time = datetime.fromtimestamp(last_activity, tz=timezone.get_current_timezone())
                elapsed_time = (timezone.now() - last_activity_time).total_seconds()
                
                if elapsed_time > settings.SESSION_COOKIE_AGE:
                    logout(request)
                    return redirect('authen:login')  # Add namespace
            
            # Store current time as timestamp
            request.session['last_activity'] = timezone.now().timestamp()

        return self.get_response(request)