from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import ContentPage


class ContentPageModelTest(TestCase):
    """Test cases for content page model."""
    
    def test_create_content_page(self):
        """Test creating a content page."""
        page = ContentPage.objects.create(
            title='Privacy Policy',
            slug='privacy-policy',
            content='This is our privacy policy content.',
            is_active=True
        )
        
        self.assertEqual(page.title, 'Privacy Policy')
        self.assertEqual(page.slug, 'privacy-policy')
        self.assertTrue(page.is_active)
    
    def test_content_page_str_representation(self):
        """Test string representation of content page."""
        page = ContentPage.objects.create(
            title='Privacy Policy',
            slug='privacy-policy',
            content='Privacy content'
        )
        
        self.assertEqual(str(page), 'Privacy Policy')


class ContentPageViewTest(TestCase):
    """Test cases for content page views."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = APIClient()
        self.active_page = ContentPage.objects.create(
            title='Privacy Policy',
            slug='privacy-policy',
            content='Privacy policy content',
            is_active=True
        )
        self.inactive_page = ContentPage.objects.create(
            title='Inactive Page',
            slug='inactive-page',
            content='Inactive content',
            is_active=False
        )
    
    def test_content_page_list_view(self):
        """Test content page list API."""
        url = reverse('content:page-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return active pages
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Privacy Policy')
    
    def test_content_page_detail_view(self):
        """Test content page detail API."""
        url = reverse('content:page-detail', kwargs={'slug': 'privacy-policy'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Privacy Policy')
    
    def test_inactive_page_not_accessible(self):
        """Test that inactive pages are not accessible."""
        url = reverse('content:page-detail', kwargs={'slug': 'inactive-page'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
