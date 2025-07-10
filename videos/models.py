from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.dispatch import receiver
import os

User = get_user_model()


class Genre(models.Model):
    """
    Video genre model.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'video_genres'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


def video_upload_path(instance, filename):
    """Generate upload path for video files."""
    return f'videos/{instance.id}/{filename}'


def thumbnail_upload_path(instance, filename):
    """Generate upload path for thumbnail files."""
    return f'thumbnails/{instance.id}/{filename}'


class Video(models.Model):
    """
    Video model for storing video content.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='videos')
    video_file = models.FileField(upload_to=video_upload_path)
    thumbnail = models.ImageField(upload_to=thumbnail_upload_path, blank=True, null=True)
    duration = models.DurationField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_videos', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'videos'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def thumbnail_url(self):
        """Get thumbnail URL or placeholder."""
        if self.thumbnail and self.thumbnail.name:
            # Check if it's a static file path (starts with /static/)
            if self.thumbnail.name.startswith('/static/'):
                return self.thumbnail.name
            # Otherwise, it's a normal media file
            else:
                return self.thumbnail.url
        return '/static/images/video-placeholder.png'


class VideoQuality(models.Model):
    """
    Different quality versions of a video.
    """
    QUALITY_CHOICES = [
        ('120p', '120p'),
        ('360p', '360p'),
        ('720p', '720p'),
        ('1080p', '1080p'),
    ]
    
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='qualities')
    quality = models.CharField(max_length=10, choices=QUALITY_CHOICES)
    file_path = models.CharField(max_length=500)
    file_size = models.BigIntegerField(default=0)
    is_ready = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'video_qualities'
        unique_together = ['video', 'quality']
    
    def __str__(self):
        return f"{self.video.title} - {self.quality}"


class WatchProgress(models.Model):
    """
    Track user's watch progress for videos.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    current_time = models.DurationField(default=0)
    is_completed = models.BooleanField(default=False)
    last_watched = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'watch_progress'
        unique_together = ['user', 'video']
    
    def __str__(self):
        return f"{self.user.email} - {self.video.title}"
    
    @property
    def progress_percentage(self):
        """Calculate watch progress percentage."""
        if not self.video.duration:
            return 0
        
        current_seconds = self.current_time.total_seconds()
        total_seconds = self.video.duration.total_seconds()
        
        if total_seconds == 0:
            return 0
        
        return min(100, (current_seconds / total_seconds) * 100)


@receiver(post_save, sender=Video)
def process_video_for_hls(sender, instance, created, **kwargs):
    """
    Automatically process uploaded videos for HLS streaming.
    Uses mentor's FFmpeg command for conversion.
    """
    if created and instance.video_file:
        # Import here to avoid circular imports
        from .hls_utils import hls_processor
        
        # Process video in background (optional)
        try:
            hls_processor.convert_to_hls(instance)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error processing video {instance.id} for HLS: {str(e)}")
