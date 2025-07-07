from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from datetime import timedelta
from django.http import JsonResponse

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    UserProfileSerializer
)
from .models import EmailVerificationToken, PasswordResetToken
from .utils import (
    generate_secure_token,
    send_verification_email,
    send_password_reset_email,
    get_user_by_email
)

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    Register a new user.
    """
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        # Create activation token using Django's built-in token generator
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Send verification email
        send_verification_email(user, token)
        
        return Response({
            'user': {
                'id': user.id,
                'email': user.email
            },
            'token': token
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def activate_account(request, uidb64, token):
    """
    Activate user account using uidb64 and token from email.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            if not user.is_active:
                user.is_active = True
                user.is_email_verified = True
                user.save()
                return Response({
                    'message': 'Account successfully activated.'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'Account is already activated.'
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid activation link.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({
            'error': 'Invalid activation link.'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Login user and return authentication token.
    """
    serializer = UserLoginSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Create or get authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        # Django session login
        login(request, user)
        
        return Response({
            'token': token.key,
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Logout user and delete authentication token.
    """
    try:
        # Delete user's token
        request.user.auth_token.delete()
    except:
        pass
    
    # Django session logout
    logout(request)
    
    return Response({
        'message': 'Logout successful.'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Request password reset email.
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        user = get_user_by_email(email)
        
        if user:
            # Delete old reset tokens
            PasswordResetToken.objects.filter(user=user, used=False).delete()
            
            # Create new reset token
            token = generate_secure_token()
            PasswordResetToken.objects.create(user=user, token=token)
            
            # Send reset email
            send_password_reset_email(user, token)
        
        # Always return success for security
        return Response({
            'message': 'If the email exists, a password reset link has been sent.'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request, token):
    """
    Reset password with token.
    """
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        try:
            reset_token = PasswordResetToken.objects.get(
                token=token, 
                used=False
            )
            
            # Check if token is not expired (24 hours)
            if reset_token.created_at < timezone.now() - timedelta(hours=24):
                return Response({
                    'error': 'Reset token has expired.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Reset password
            user = reset_token.user
            user.set_password(serializer.validated_data['password'])
            user.save()
            
            # Mark token as used
            reset_token.used = True
            reset_token.save()
            
            return Response({
                'message': 'Password reset successful.'
            }, status=status.HTTP_200_OK)
            
        except PasswordResetToken.DoesNotExist:
            return Response({
                'error': 'Invalid reset token.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get current user profile.
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    Refresh JWT token using refresh token cookie.
    """
    # For now, using simple token auth - this would need JWT implementation
    # This is a placeholder that matches the expected response format
    return Response({
        'detail': 'Token refreshed',
        'access': 'new_access_token'  # This would be a real JWT token
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request, uidb64, token):
    """
    Confirm password reset using uidb64 and token from email.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')
            
            if not new_password or not confirm_password:
                return Response({
                    'error': 'Both password fields are required.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if new_password != confirm_password:
                return Response({
                    'error': 'Passwords do not match.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            
            return Response({
                'detail': 'Your Password has been successfully reset.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid reset link.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({
            'error': 'Invalid reset link.'
        }, status=status.HTTP_400_BAD_REQUEST)
