import secrets
import string
from typing import Optional, TYPE_CHECKING
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

User = get_user_model()


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    
    Args:
        length: Length of the token to generate
        
    Returns:
        Secure random token string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_verification_email(user, uidb64: str, token: str) -> bool:
    """
    Send email verification email to user.
    
    Args:
        user: User instance
        uidb64: Base64 encoded user ID
        token: Verification token
        
    Returns:
        True if email sent successfully, False otherwise
    """
    import logging
    try:
        subject = 'Verify your Videoflix account'
        # Use configurable BACKEND_URL for mentor testing
        backend_url = getattr(settings, 'BACKEND_URL', 'http://localhost:8000')
        verification_url = f"{backend_url}/api/activate/{uidb64}/{token}"

        html_message = render_to_string('emails/verify_email.html', {
            'user': user,
            'verification_url': verification_url,
        })
        plain_message = strip_tags(html_message)

        response = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
        )
        logging.info(f"send_mail response: {response}")
        return True
    except Exception as e:
        logging.error(f"Error sending verification email: {e}")
        return False


def send_password_reset_email(user, uidb64: str, token: str) -> bool:
    """
    Send password reset email to user.
    
    Args:
        user: User instance
        uidb64: Base64 encoded user ID
        token: Reset token
        
    Returns:
        True if email sent successfully, False otherwise
    """
    try:
        subject = 'Reset your Videoflix password'
        reset_url = f"{settings.FRONTEND_URL}/password-confirm/{uidb64}/{token}"
        
        html_message = render_to_string('emails/password_reset.html', {
            'user': user,
            'reset_url': reset_url,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
        )
        return True
    except Exception:
        return False


def is_valid_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def get_user_by_email(email: str):
    """
    Get user by email address.
    
    Args:
        email: Email address
        
    Returns:
        User instance if found, None otherwise
    """
    try:
        return User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return None


def is_password_strong(password: str) -> bool:
    """
    Check if password meets strength requirements.
    
    Args:
        password: Password to check
        
    Returns:
        True if password is strong enough, False otherwise
    """
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    return has_upper and has_lower and has_digit
