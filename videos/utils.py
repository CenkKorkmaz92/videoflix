import os
import subprocess
from django.conf import settings
from django.core.files.base import ContentFile
from .models import Video, VideoQuality
import logging

logger = logging.getLogger(__name__)


def get_video_duration(video_path: str) -> float:
    """
    Get video duration using ffprobe.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Duration in seconds
    """
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-show_entries', 
            'format=duration', '-of', 'csv=p=0', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())
    except Exception as e:
        logger.error(f"Error getting video duration: {e}")
        return 0.0


def extract_thumbnail(video_path: str, thumbnail_path: str, time_offset: str = "00:00:01") -> bool:
    """
    Extract thumbnail from video at specified time.
    
    Args:
        video_path: Path to source video
        thumbnail_path: Path for output thumbnail
        time_offset: Time position to extract thumbnail
        
    Returns:
        True if successful, False otherwise
    """
    try:
        cmd = [
            'ffmpeg', '-i', video_path, '-ss', time_offset,
            '-vframes', '1', '-q:v', '2', '-y', thumbnail_path
        ]
        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error extracting thumbnail: {e}")
        return False


def convert_video_quality(input_path: str, output_path: str, quality: str) -> bool:
    """
    Convert video to specified quality.
    
    Args:
        input_path: Source video path
        output_path: Output video path
        quality: Target quality (120p, 360p, 720p, 1080p)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        quality_settings = settings.VIDEO_QUALITIES.get(quality)
        if not quality_settings:
            return False
        
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vf', f"scale={quality_settings['width']}:{quality_settings['height']}",
            '-b:v', quality_settings['bitrate'],
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-preset', 'medium',
            '-y', output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error converting video quality: {e}")
        return False


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes
    """
    try:
        return os.path.getsize(file_path)
    except Exception:
        return 0


def clean_filename(filename: str) -> str:
    """
    Clean filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename
    """
    # Remove unsafe characters
    import re
    filename = re.sub(r'[^\w\s-.]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    return filename.lower()


def is_video_file(filename: str) -> bool:
    """
    Check if file is a supported video format.
    
    Args:
        filename: File name to check
        
    Returns:
        True if supported video format, False otherwise
    """
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
    return any(filename.lower().endswith(ext) for ext in video_extensions)


def process_video_task(video_id: int) -> None:
    """
    Background task to process uploaded video.
    
    Args:
        video_id: ID of video to process
    """
    try:
        video = Video.objects.get(id=video_id)
        
        if not video.video_file:
            logger.error(f"No video file found for video {video_id}")
            return
        
        video_path = video.video_file.path
        
        # Get video duration
        duration = get_video_duration(video_path)
        video.duration = duration
        
        # Extract and save thumbnail if not provided
        if not video.thumbnail:
            thumbnail_filename = f"thumb_{video.id}.jpg"
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', thumbnail_filename)
            
            # Create thumbnails directory if it doesn't exist
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            
            if extract_thumbnail(video_path, thumbnail_path):
                with open(thumbnail_path, 'rb') as thumb_file:
                    video.thumbnail.save(
                        thumbnail_filename,
                        ContentFile(thumb_file.read()),
                        save=False
                    )
        
        # Process different quality versions
        quality_settings = getattr(settings, 'VIDEO_QUALITIES', {
            '360p': {'width': 640, 'height': 360, 'bitrate': '800k'},
            '720p': {'width': 1280, 'height': 720, 'bitrate': '2500k'},
            '1080p': {'width': 1920, 'height': 1080, 'bitrate': '5000k'},
        })
        
        for quality, settings_dict in quality_settings.items():
            try:
                # Generate output filename
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                output_filename = f"{base_name}_{quality}.mp4"
                output_path = os.path.join(
                    settings.MEDIA_ROOT, 
                    'videos', 
                    'processed', 
                    output_filename
                )
                
                # Create processed videos directory if it doesn't exist
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Convert video
                if convert_video_quality(video_path, output_path, quality):
                    # Create VideoQuality record
                    VideoQuality.objects.create(
                        video=video,
                        quality=quality,
                        file_size=get_file_size(output_path),
                        is_ready=True
                    )
                    logger.info(f"Successfully processed {quality} for video {video_id}")
                else:
                    logger.error(f"Failed to process {quality} for video {video_id}")
                    
            except Exception as e:
                logger.error(f"Error processing {quality} for video {video_id}: {e}")
        
        # Mark video as processed
        video.is_processed = True
        video.save()
        
        logger.info(f"Video {video_id} processing completed successfully")
        
    except Video.DoesNotExist:
        logger.error(f"Video {video_id} not found")
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {e}")
