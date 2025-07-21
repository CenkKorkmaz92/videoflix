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
    convert_to_hls_segments,
    get_directory_size,
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
        
        duration_seconds = get_video_duration(video_path)
        if duration_seconds > 0:
            video.duration = timedelta(seconds=duration_seconds)
        
        if not video.thumbnail:
            thumbnail_filename = f"thumb_{video.id}.jpg"
            thumbnail_path = os.path.join(
                settings.MEDIA_ROOT,
                'thumbnails',
                str(video.id),
                thumbnail_filename
            )
            
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            
            if extract_thumbnail(video_path, thumbnail_path):
                with open(thumbnail_path, 'rb') as thumb_file:
                    video.thumbnail.save(
                        thumbnail_filename,
                        ContentFile(thumb_file.read()),
                        save=False
                    )
        
        create_video_qualities(video_id)
        
        video.is_processed = True
        video.save()
        
        logger.info(f"Successfully processed video: {video.title}")
        
    except Video.DoesNotExist:
        logger.error(f"Video with ID {video_id} not found")
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {e}")


@django_rq.job('default', timeout=3600)
def create_video_qualities(video_id: int):
    """
    Background task to create different quality versions of video.
    
    Args:
        video_id: ID of the video to process
    """
    try:
        video = Video.objects.get(id=video_id)
        source_path = video.video_file.path
        
        qualities = ['480p', '720p', '1080p']
        
        for quality in qualities:
            if VideoQuality.objects.filter(video=video, quality=quality).exists():
                continue
            
            # Create HLS segments for each quality instead of MP4 files
            hls_output_dir = os.path.join(
                settings.MEDIA_ROOT,
                'videos',
                str(video.id),
                'hls',
                quality
            )
            os.makedirs(hls_output_dir, exist_ok=True)
            
            if convert_to_hls_segments(source_path, hls_output_dir, quality):
                m3u8_path = os.path.join(hls_output_dir, 'index.m3u8')
                
                if os.path.exists(m3u8_path):
                    file_size = get_directory_size(hls_output_dir)
                    
                    VideoQuality.objects.create(
                        video=video,
                        quality=quality,
                        file_path=hls_output_dir,  # Directory path, not file
                        file_size=file_size,
                        is_ready=True
                    )
                    
                    logger.info(f"Created HLS {quality} quality for video: {video.title}")
                else:
                    logger.error(f"HLS manifest not found for {quality}: {m3u8_path}")
            else:
                logger.error(f"Failed to create HLS {quality} for video: {video.title}")
        
        video.is_processed = True
        video.save()
        
        # Extract actual video thumbnail after processing is complete
        if not video.thumbnail:
            thumbnail_filename = f"thumb_{video.id}.jpg"
            thumbnail_path = os.path.join(
                settings.MEDIA_ROOT,
                'thumbnails',
                thumbnail_filename
            )
            
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            
            if extract_thumbnail(source_path, thumbnail_path, time_offset="00:00:02"):
                with open(thumbnail_path, 'rb') as thumb_file:
                    video.thumbnail.save(
                        thumbnail_filename,
                        ContentFile(thumb_file.read()),
                        save=True
                    )
                logger.info(f"Generated video thumbnail for: {video.title}")
            else:
                logger.warning(f"Could not extract thumbnail for: {video.title}")
        
        logger.info(f"Video {video.title} marked as processed - all qualities created!")
        
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
        
        total_qualities = 3
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
