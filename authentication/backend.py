from django.contrib.auth.backends import ModelBackend
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(username=username)
            
            # Check if user is blocked
            if user.failed_login_attempts >= 3 and user.last_failed_login:
                block_period = timezone.now() - user.last_failed_login
                if block_period.total_seconds() < 180:  # 3 minutes
                    return None
            
            if user.check_password(password):
                user.reset_failed_login()
                return user
            else:
                user.increment_failed_login()
                return None
                
        except CustomUser.DoesNotExist:
            return None