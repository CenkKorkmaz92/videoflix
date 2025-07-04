from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for custom user model."""
    
    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_email_verified)
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.assertEqual(admin_user.email, 'admin@example.com')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_email_verified)
    
    def test_user_str_representation(self):
        """Test string representation of user."""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.assertEqual(str(user), 'test@example.com')


class AuthenticationViewTest(TestCase):
    """Test cases for authentication views."""
    
    def setUp(self):
        """Set up test client and user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            is_email_verified=True
        )
    
    def test_user_registration(self):
        """Test user registration."""
        url = reverse('authentication:register')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        
        with patch('authentication.views.send_verification_email'):
            response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
    
    def test_user_login(self):
        """Test user login."""
        url = reverse('authentication:login')
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_password_reset_request(self):
        """Test password reset request."""
        url = reverse('authentication:password-reset')
        data = {'email': 'test@example.com'}
        
        with patch('authentication.views.send_password_reset_email'):
            response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_invalid_login(self):
        """Test login with invalid credentials."""
        url = reverse('authentication:login')
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
