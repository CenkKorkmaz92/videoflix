from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from .models import Video, Genre, WatchProgress

User = get_user_model()


class VideoModelTest(TestCase):
    """Test cases for video model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.genre = Genre.objects.create(name='Action')
    
    def test_create_video(self):
        """Test creating a video."""
        video = Video.objects.create(
            title='Test Video',
            description='Test description',
            genre=self.genre,
            uploaded_by=self.user
        )
        
        self.assertEqual(video.title, 'Test Video')
        self.assertEqual(video.genre, self.genre)
        self.assertEqual(video.uploaded_by, self.user)
        self.assertFalse(video.is_processed)
    
    def test_video_str_representation(self):
        """Test string representation of video."""
        video = Video.objects.create(
            title='Test Video',
            genre=self.genre,
            uploaded_by=self.user
        )
        
        self.assertEqual(str(video), 'Test Video')
    
    def test_genre_slug_generation(self):
        """Test genre slug auto-generation."""
        genre = Genre.objects.create(name='Science Fiction')
        self.assertEqual(genre.slug, 'science-fiction')


class VideoViewTest(TestCase):
    """Test cases for video views."""
    
    def setUp(self):
        """Set up test client and data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.genre = Genre.objects.create(name='Action')
        self.video = Video.objects.create(
            title='Test Video',
            description='Test description',
            genre=self.genre,
            uploaded_by=self.user,
            is_processed=True
        )
    
    def test_video_list_view(self):
        """Test video list API."""
        url = reverse('videos:video-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Test Video')
    
    def test_video_detail_view(self):
        """Test video detail API."""
        url = reverse('videos:video-detail', kwargs={'pk': self.video.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Video')
    
    def test_video_upload_authenticated(self):
        """Test video upload with authentication."""
        self.client.force_authenticate(user=self.user)
        url = reverse('videos:video-upload')
        
        video_file = SimpleUploadedFile(
            "test.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        data = {
            'title': 'New Video',
            'description': 'New description',
            'genre_id': self.genre.id,
            'video_file': video_file
        }
        
        with patch('django_rq.get_queue') as mock_queue:
            mock_queue.return_value.enqueue = MagicMock()
            response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_video_upload_unauthenticated(self):
        """Test video upload without authentication."""
        url = reverse('videos:video-upload')
        data = {
            'title': 'New Video',
            'description': 'New description',
            'genre_id': self.genre.id
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_content_page_list_view(self):
        """Test content page list view."""
        self.client.force_authenticate(user=self.user)
        url = reverse('videos:video-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertEqual(len(response.data), 1)
    
    def test_dashboard_data(self):
        """Test dashboard data API."""
        url = reverse('videos:dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('hero_video', response.data)
        self.assertIn('genres', response.data)
