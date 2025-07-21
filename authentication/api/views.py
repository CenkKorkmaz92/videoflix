from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.conf import settings

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    UserProfileSerializer
)
from ..models import EmailVerificationToken
from ..utils import (
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
        
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        
        if isinstance(uidb64, bytes):
            uidb64 = uidb64.decode()
        
        send_verification_email(user, uidb64, token)
        
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
    Returns JSON response for frontend API consumption.
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
                    'message': 'Account successfully activated!',
                    'status': 'success'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'Account already activated',
                    'status': 'already_active'
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'Invalid or expired activation link',
                'status': 'invalid'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({
            'message': 'Invalid activation link',
            'status': 'error'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user and return JWT tokens with HttpOnly cookies."""
    content_type = request.content_type
    if content_type and 'application/json' not in content_type:
        return Response({
            'detail': 'Content-Type must be application/json'
        }, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    
    serializer = UserLoginSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        response_data = {
            'detail': 'Login successful',
            'user': {'id': user.id, 'username': user.email}
        }
        response = Response(response_data, status=status.HTTP_200_OK)
        
        response.set_cookie('access_token', str(access_token), max_age=3600, httponly=True)
        response.set_cookie('refresh_token', str(refresh), max_age=604800, httponly=True)
        return response
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_user(request):
    """
    Logout user and clear JWT cookies.
    Requires refresh token cookie.
    """
    refresh_token = request.COOKIES.get('refresh_token')
    
    if not refresh_token:
        return Response({
            'detail': 'Refresh token is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        response = Response({
            'detail': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
        response.delete_cookie(
            'access_token',
            path='/',
            samesite='Lax'
        )
        response.delete_cookie(
            'refresh_token',
            path='/',
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        response = Response({
            'detail': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
        response.delete_cookie(
            'access_token',
            path='/',
            samesite='Lax'
        )
        response.delete_cookie(
            'refresh_token',
            path='/',
            samesite='Lax'
        )
        
        return response


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
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            
            if isinstance(uidb64, bytes):
                uidb64 = uidb64.decode()
            
            send_password_reset_email(user, uidb64, token)
            
            return Response({
                'detail': 'An email has been sent to reset your password.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': 'No user found with this email address.'
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
    Refresh JWT access token using refresh token cookie.
    Returns new access token and sets it as HttpOnly cookie.
    """
    refresh_token_value = request.COOKIES.get('refresh_token')
    
    if not refresh_token_value:
        return Response({
            'detail': 'Refresh token is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh_token = RefreshToken(refresh_token_value)
        
        new_access_token = refresh_token.access_token
        
        response_data = {
            'detail': 'Token refreshed successfully',
            'access': str(new_access_token)
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        
        response.set_cookie(
            'access_token',
            str(new_access_token),
            max_age=3600,
            httponly=True,
            secure=False,
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        return Response({
            'detail': 'Invalid or expired refresh token.'
        }, status=status.HTTP_401_UNAUTHORIZED)


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


@api_view(['GET'])
@permission_classes([AllowAny])
def get_reset_token_for_testing(request, uidb64):
    """
    Test-only endpoint to get reset token for a user.
    Only available in DEBUG mode for testing purposes.
    """
    if not settings.DEBUG:
        return Response(
            {'detail': 'This endpoint is only available in debug mode.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        token = default_token_generator.make_token(user)
        
        return Response({
            'reset_token': token,
            'uidb64': uidb64,
            'user_id': user.id
        }, status=status.HTTP_200_OK)
        
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'detail': 'Invalid user ID.'},
            status=status.HTTP_400_BAD_REQUEST
        )
