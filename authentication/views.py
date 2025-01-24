from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from .models import CustomUser, UserProfile, MFAToken
from .forms import CustomUserCreationForm, UserProfileForm, MFAVerificationForm
import random
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

class EmailVerification:
    @staticmethod
    def send_verification_email(user, token):
        subject = 'Login Verification Code'
        message = f'Your verification code is: {token}'
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully. Please login.')
            return redirect('authentication:login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'authentication/register.html', {'form': form})

def verify_mfa(request):
    user_id = request.session.get('mfa_user_id')
    if not user_id:
        return redirect('authentication:login')
    
    if request.method == 'POST':
        form = MFAVerificationForm(request.POST)
        if form.is_valid():
            token = form.cleaned_data['token']
            user = CustomUser.objects.get(id=user_id)
            
            try:
                mfa_token = MFAToken.objects.get(
                    user=user,
                    token=token,
                    is_used=False,
                    created_at__gte=timezone.now() - timezone.timedelta(minutes=10)
                )
                mfa_token.is_used = True
                mfa_token.save()
                login(request, user)
                del request.session['mfa_user_id']
                return redirect('authentication:profile')
            except MFAToken.DoesNotExist:
                messages.error(request, 'Invalid or expired token')
    else:
        form = MFAVerificationForm()
    
    return render(request, 'authentication/verify_mfa.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            mfa_token = MFAToken.generate_token(user)
            EmailVerification.send_verification_email(user, mfa_token.token)
            request.session['mfa_user_id'] = user.id
            return redirect('authentication:verify_mfa')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'authentication/login.html')



@login_required
def profile_view(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('authentication:profile')
    else:
        form = UserProfileForm(instance=user_profile)
    
    return render(request, 'authentication/profile.html', {'form': form})

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            # Generate password reset token
            token = ''.join(random.choices('0123456789ABCDEF', k=32))
            user.password_reset_token = token
            user.password_reset_expires = timezone.now() + timezone.timedelta(hours=24)
            user.save()
            
            # Send reset email
            reset_url = request.build_absolute_uri(
                reverse('authentication:reset_password', args=[token])
            )
            send_mail(
                'Password Reset Request',
                f'Click here to reset your password: {reset_url}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Password reset link sent to your email')
            return redirect('authentication:login')
        except CustomUser.DoesNotExist:
            messages.error(request, 'No user found with that email')
    
    return render(request, 'authentication/forgot_password.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('authentication:login')

def reset_password(request, token):
    try:
        user = CustomUser.objects.get(
            password_reset_token=token,
            password_reset_expires__gt=timezone.now()
        )
    except CustomUser.DoesNotExist:
        messages.error(request, 'Invalid or expired reset link')
        return redirect('authentication:login')
    
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
        else:
            user.set_password(password1)
            user.password_reset_token = None
            user.password_reset_expires = None
            user.save()
            messages.success(request, 'Password reset successfully')
            return redirect('authentication:login')
            
    return render(request, 'authentication/reset_password.html')

@login_required
def profile_list(request):
    """View all profiles (Read - List)"""
    profiles = UserProfile.objects.all()
    return render(request, 'authentication/profile_list.html', {'profiles': profiles})

@login_required
def profile_detail(request, pk):
    """View single profile (Read - Detail)"""
    profile = get_object_or_404(UserProfile, pk=pk)
    return render(request, 'authentication/profile_detail.html', {'profile': profile})

@login_required
def profile_create(request):
    """Create new profile (Create)"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Profile created successfully')
            return redirect('authentication:profile_detail', pk=profile.pk)
    else:
        form = UserProfileForm()
    return render(request, 'authentication/profile_form.html', {'form': form, 'action': 'Create'})

@login_required
def profile_update(request, pk):
    """Update existing profile (Update)"""
    profile = get_object_or_404(UserProfile, pk=pk)
    
    # Check if user is authorized to edit this profile
    if profile.user != request.user and not request.user.is_staff:
        messages.error(request, 'You are not authorized to edit this profile')
        return redirect('authentication:profile_list')
        
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('authentication:profile_detail', pk=profile.pk)
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'authentication/profile_form.html', {'form': form, 'action': 'Update'})

@login_required
def profile_delete(request, pk):
    """Delete profile (Delete)"""
    profile = get_object_or_404(UserProfile, pk=pk)
    
    # Check if user is authorized to delete this profile
    if profile.user != request.user and not request.user.is_staff:
        messages.error(request, 'You are not authorized to delete this profile')
        return redirect('authentication:profile_list')
        
    if request.method == 'POST':
        profile.delete()
        messages.success(request, 'Profile deleted successfully')
        return redirect('authentication:profile_list')
    return render(request, 'authentication/profile_confirm_delete.html', {'profile': profile})