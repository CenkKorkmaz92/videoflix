from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .utils import is_valid_email, is_password_strong

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'}
    )
    confirmed_password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'confirmed_password']
    
    def validate_email(self, value):
        """Validate email format and uniqueness."""
        if not is_valid_email(value):
            raise serializers.ValidationError("Invalid email format.")
        
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Please check your input and try again."
            )
        
        return value.lower()
    
    def validate_password(self, value):
        """Validate password strength."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        
        if not is_password_strong(value):
            raise serializers.ValidationError(
                "Password must contain uppercase, lowercase, and numeric characters."
            )
        
        return value
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['confirmed_password']:
            raise serializers.ValidationError({
                'confirmed_password': 'Passwords do not match.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """Create new user."""
        validated_data.pop('confirmed_password')
        # Create inactive user - account remains inactive until email verification
        validated_data['is_active'] = False
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        """Authenticate user credentials."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Please check your input and try again.'
                )
            
            if not user.is_email_verified:
                raise serializers.ValidationError(
                    'Please verify your email before logging in.'
                )
            
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError(
            'Please provide both email and password.'
        )


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    """
    email = serializers.EmailField()
    
    def validate_email(self, value):
        """Validate email format."""
        if not is_valid_email(value):
            raise serializers.ValidationError("Invalid email format.")
        return value.lower()


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset.
    """
    token = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate_password(self, value):
        """Validate password strength."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        
        if not is_password_strong(value):
            raise serializers.ValidationError(
                "Password must contain uppercase, lowercase, and numeric characters."
            )
        
        return value
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    """
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'is_email_verified', 'date_joined']
        read_only_fields = ['id', 'email', 'is_email_verified', 'date_joined']
