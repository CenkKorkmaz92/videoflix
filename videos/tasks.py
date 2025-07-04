import os
import django_rq
from django.conf import settings
from django.core.files.base import ContentFile
from datetime import timedelta
from .models import Video, VideoQuality
from .utils import (
    get_video_duration,
    extract_thumbnail,
    convert_video_quality,
    get_file_size,
    clean_filename
)
import logging

logger = logging.getLogger(__name__)


def process_video_upload(video_id: int):
    """
    Background task to process uploaded video.
    
    Args:
        video_id: ID of the video to process
    """
    try:
        video = Video.objects.get(id=video_id)
        video_path = video.video_file.path
        
        # Get video duration
        duration_seconds = get_video_duration(video_path)
        if duration_seconds > 0:
            video.duration = timedelta(seconds=duration_seconds)
        
        # Extract thumbnail if not provided
        if not video.thumbnail:
            thumbnail_filename = f"thumb_{video.id}.jpg"
            thumbnail_path = os.path.join(
                settings.MEDIA_ROOT, 
                'thumbnails', 
                str(video.id), 
                thumbnail_filename
            )
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            
            if extract_thumbnail(video_path, thumbnail_path):
                with open(thumbnail_path, 'rb') as thumb_file:
                    video.thumbnail.save(
                        thumbnail_filename,
                        ContentFile(thumb_file.read()),
                        save=False
                    )
        
        # Create different quality versions
        create_video_qualities.delay(video_id)
        
        video.is_processed = True
        video.save()
        
        logger.info(f"Successfully processed video: {video.title}")
        
    except Video.DoesNotExist:
        logger.error(f"Video with ID {video_id} not found")
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {e}")


@django_rq.job('default', timeout=3600)  # 1 hour timeout
def create_video_qualities(video_id: int):
    """
    Background task to create different quality versions of video.
    
    Args:
        video_id: ID of the video to process
    """
    try:
        video = Video.objects.get(id=video_id)
        source_path = video.video_file.path
        
        qualities = ['120p', '360p', '720p', '1080p']
        
        for quality in qualities:
            # Skip if quality already exists
            if VideoQuality.objects.filter(video=video, quality=quality).exists():
                continue
            
            # Create output directory
            output_dir = os.path.join(
                settings.MEDIA_ROOT, 
                'videos', 
                str(video.id), 
                'qualities'
            )
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate output filename
            base_name = clean_filename(os.path.splitext(video.video_file.name)[0])
            output_filename = f"{base_name}_{quality}.mp4"
            output_path = os.path.join(output_dir, output_filename)
            
            # Convert video
            if convert_video_quality(source_path, output_path, quality):
                # Get file size
                file_size = get_file_size(output_path)
                
                # Create VideoQuality record
                VideoQuality.objects.create(
                    video=video,
                    quality=quality,
                    file_path=output_path,
                    file_size=file_size,
                    is_ready=True
                )
                
                logger.info(f"Created {quality} version for video: {video.title}")
            else:
                logger.error(f"Failed to create {quality} version for video: {video.title}")
        
        logger.info(f"Finished processing qualities for video: {video.title}")
        
    except Video.DoesNotExist:
        logger.error(f"Video with ID {video_id} not found")
    except Exception as e:
        logger.error(f"Error creating video qualities for {video_id}: {e}")


def queue_video_processing(video_id: int):
    """
    Queue video processing task.
    
    Args:
        video_id: ID of the video to process
    """
    queue = django_rq.get_queue('default')
    queue.enqueue(process_video_upload, video_id)


def get_processing_status(video_id: int) -> dict:
    """
    Get processing status for a video.
    
    Args:
        video_id: ID of the video
        
    Returns:
        Dictionary with processing status information
    """
    try:
        video = Video.objects.get(id=video_id)
        qualities = VideoQuality.objects.filter(video=video)
        
        total_qualities = 4  # 120p, 360p, 720p, 1080p
        ready_qualities = qualities.filter(is_ready=True).count()
        
        return {
            'is_processed': video.is_processed,
            'qualities_ready': ready_qualities,
            'total_qualities': total_qualities,
            'progress_percentage': (ready_qualities / total_qualities) * 100,
            'available_qualities': list(qualities.filter(is_ready=True).values_list('quality', flat=True))
        }
    
    except Video.DoesNotExist:
        return {
            'is_processed': False,
            'qualities_ready': 0,
            'total_qualities': 0,
            'progress_percentage': 0,
            'available_qualities': []
        }
