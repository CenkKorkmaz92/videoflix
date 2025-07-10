"""
Custom authentication classes for JWT with HttpOnly cookies.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model

User = get_user_model()


class JWTCookieAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads tokens from HttpOnly cookies.
    """
    
    def authenticate(self, request):
        # Try to get token from cookies
        access_token = request.COOKIES.get('access_token')
        
        if access_token is None:
            return None
        
        try:
            # Validate the token
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
            return user, validated_token
        except TokenError:
            return None
    
    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        try:
            return AccessToken(raw_token)
        except TokenError as e:
            raise InvalidToken({
                'detail': 'Given token not valid for any token type',
                'messages': [{'token_class': 'AccessToken', 'token_type': 'access', 'message': str(e)}],
            })

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token['user_id']
        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')

        try:
            user = User.objects.get(**{'id': user_id})
        except User.DoesNotExist:
            raise InvalidToken('User not found')

        if not user.is_active:
            raise InvalidToken('User is inactive')

        return user
