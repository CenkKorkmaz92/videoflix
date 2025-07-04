from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

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
        
        # Create verification token
        token = generate_secure_token()
        EmailVerificationToken.objects.create(user=user, token=token)
        
        # Send verification email
        send_verification_email(user, token)
        
        return Response({
            'message': 'Registration successful. Please check your email to verify your account.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request, token):
    """
    Verify user email with token.
    """
    try:
        verification_token = EmailVerificationToken.objects.get(token=token)
        user = verification_token.user
        
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save()
            verification_token.delete()
            
            return Response({
                'message': 'Email verified successfully.'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'Email already verified.'
        }, status=status.HTTP_200_OK)
        
    except EmailVerificationToken.DoesNotExist:
        return Response({
            'error': 'Invalid verification token.'
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
