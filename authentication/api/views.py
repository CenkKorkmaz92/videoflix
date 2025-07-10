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
from .models import EmailVerificationToken
from .utils import (
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
        
        # Convert uidb64 to string if it's bytes
        if isinstance(uidb64, bytes):
            uidb64 = uidb64.decode()
        
        # Send verification email
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
                    'detail': 'Account activated successfully'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'detail': 'Account is already activated.'
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
    Login user and return JWT tokens with HttpOnly cookies.
    Only accepts JSON content type.
    """
    # Check content type
    content_type = request.content_type
    if content_type and 'application/json' not in content_type:
        return Response({
            'detail': 'Content-Type must be application/json'
        }, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    
    serializer = UserLoginSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Create response with required format
        response_data = {
            'detail': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.email  # Using email as username as per documentation
            }
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        
        # Set HttpOnly cookies for tokens
        response.set_cookie(
            'access_token',
            str(access_token),
            max_age=3600,  # 1 hour
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Lax'
        )
        
        response.set_cookie(
            'refresh_token',
            str(refresh),
            max_age=604800,  # 7 days
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Lax'
        )
        
        return response
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_user(request):
    """
    Logout user and clear JWT cookies.
    Requires refresh token cookie.
    """
    # Check if refresh token exists in cookies
    refresh_token = request.COOKIES.get('refresh_token')
    
    if not refresh_token:
        return Response({
            'detail': 'Refresh token is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Try to blacklist the refresh token
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        # Create success response
        response = Response({
            'detail': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
        # Clear cookies with proper attributes
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
        # If token is invalid or already blacklisted, still clear cookies and return success
        # This prevents enumeration attacks and provides better UX
        response = Response({
            'detail': 'Logout successful'
        }, status=status.HTTP_200_OK)
        
        # Clear cookies anyway
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
            # Create reset token using Django's built-in token generator (same as activation)
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Convert uidb64 to string if it's bytes
            if isinstance(uidb64, bytes):
                uidb64 = uidb64.decode()
            
            # Send reset email with uidb64 and token
            send_password_reset_email(user, uidb64, token)
            
            # Return success only if user exists
            return Response({
                'detail': 'An email has been sent to reset your password.'
            }, status=status.HTTP_200_OK)
        else:
            # Return error if email doesn't exist (as per API specification)
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
    # Check if refresh token exists in cookies
    refresh_token_value = request.COOKIES.get('refresh_token')
    
    if not refresh_token_value:
        return Response({
            'detail': 'Refresh token is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Validate and decode the refresh token
        refresh_token = RefreshToken(refresh_token_value)
        
        # Generate new access token from the refresh token
        new_access_token = refresh_token.access_token
        
        # Create response with required format
        response_data = {
            'detail': 'Token refreshed successfully',
            'access': str(new_access_token)
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        
        # Set new access token as HttpOnly cookie
        response.set_cookie(
            'access_token',
            str(new_access_token),
            max_age=3600,  # 1 hour
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        # Invalid or expired refresh token
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
        # Decode the user ID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        
        # Generate reset token
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
