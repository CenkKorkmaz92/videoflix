import os
import subprocess
import logging
from django.conf import settings
from django.core.files.base import ContentFile
from .models import Video, VideoQuality

logger = logging.getLogger(__name__)


def check_ffmpeg_installed() -> bool:
    """
    Check if FFmpeg is installed and available.
    
    Returns:
        True if FFmpeg is available, False otherwise
    """
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_video_info(video_path: str) -> dict:
    """
    Get video information using ffprobe.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with video information
    """
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
        else:
            logger.error(f"ffprobe failed: {result.stderr}")
            return {}
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return {}


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
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())
        return 0.0
    except Exception as e:
        logger.error(f"Error getting video duration: {e}")
        return 0.0


def extract_thumbnail(video_path: str, thumbnail_path: str, time_offset: str = "00:00:01") -> bool:
    """
    Extract thumbnail from video at specified time using FFmpeg.
    
    Args:
        video_path: Path to source video
        thumbnail_path: Path for output thumbnail
        time_offset: Time position to extract thumbnail (default: 1 second)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        
        cmd = [
            'ffmpeg', '-i', video_path, 
            '-ss', time_offset,          # Seek to time position
            '-vframes', '1',             # Extract 1 frame
            '-q:v', '2',                 # High quality
            '-vf', 'scale=320:240',      # Resize to standard thumbnail size
            '-y', thumbnail_path         # Overwrite if exists
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(thumbnail_path):
            logger.info(f"Thumbnail extracted successfully: {thumbnail_path}")
            return True
        else:
            logger.error(f"FFmpeg thumbnail extraction failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"Thumbnail extraction timed out for: {video_path}")
        return False
    except Exception as e:
        logger.error(f"Error extracting thumbnail: {e}")
        return False


def convert_video_quality(input_path: str, output_path: str, quality: str) -> bool:
    """
    Convert video to specified quality using FFmpeg.
    
    Args:
        input_path: Source video path
        output_path: Output video path
        quality: Target quality (480p, 720p, 1080p)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Quality settings
        quality_settings = {
            '480p': {'width': 854, 'height': 480, 'bitrate': '1000k'},
            '720p': {'width': 1280, 'height': 720, 'bitrate': '2500k'},
            '1080p': {'width': 1920, 'height': 1080, 'bitrate': '5000k'},
        }
        
        if quality not in quality_settings:
            logger.error(f"Unsupported quality: {quality}")
            return False
        
        settings_dict = quality_settings[quality]
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264',                                    # Video codec
            '-preset', 'medium',                                  # Encoding speed/quality balance
            '-crf', '23',                                         # Constant rate factor (quality)
            '-vf', f"scale={settings_dict['width']}:{settings_dict['height']}", # Scale video
            '-b:v', settings_dict['bitrate'],                     # Video bitrate
            '-c:a', 'aac',                                        # Audio codec
            '-b:a', '128k',                                       # Audio bitrate
            '-movflags', '+faststart',                            # Web optimization
            '-y', output_path                                     # Overwrite if exists
        ]
        
        logger.info(f"Starting video conversion to {quality}: {output_path}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 minute timeout
        
        if result.returncode == 0 and os.path.exists(output_path):
            logger.info(f"Video conversion successful: {quality} - {output_path}")
            return True
        else:
            logger.error(f"FFmpeg conversion failed for {quality}: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"Video conversion timed out for {quality}: {input_path}")
        return False
    except Exception as e:
        logger.error(f"Error converting video quality {quality}: {e}")
        return False


def convert_to_hls(input_path: str, output_dir: str, quality: str) -> bool:
    """
    Convert video to HLS (HTTP Live Streaming) format.
    
    Args:
        input_path: Source video path
        output_dir: Output directory for HLS files
        quality: Target quality (480p, 720p, 1080p)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        quality_settings = {
            '480p': {'width': 854, 'height': 480, 'bitrate': '1000k'},
            '720p': {'width': 1280, 'height': 720, 'bitrate': '2500k'},
            '1080p': {'width': 1920, 'height': 1080, 'bitrate': '5000k'},
        }
        
        if quality not in quality_settings:
            return False
        
        settings_dict = quality_settings[quality]
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        playlist_path = os.path.join(output_dir, f"{quality}.m3u8")
        
        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-vf', f"scale={settings_dict['width']}:{settings_dict['height']}",
            '-b:v', settings_dict['bitrate'],
            '-c:a', 'aac',
            '-b:a', '128k',
            '-hls_time', '10',                    # 10 second segments
            '-hls_list_size', '0',                # Keep all segments
            '-hls_flags', 'single_file',          # Single file output
            '-y', playlist_path
        ]
        
        logger.info(f"Converting to HLS format: {quality}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        
        if result.returncode == 0 and os.path.exists(playlist_path):
            logger.info(f"HLS conversion successful: {quality}")
            return True
        else:
            logger.error(f"HLS conversion failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error converting to HLS: {e}")
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
    filename = re.sub(r'[^\w\s\-.]', '', filename)
    filename = re.sub(r'[\-\s]+', '-', filename)
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


def process_video_task(video_id):
    """
    Background task to process video files.
    This function runs in the background using Django RQ.
    
    Args:
        video_id: ID of the video to process
    """
    try:
        video = Video.objects.get(id=video_id)
        
        if not video.video_file:
            logger.error(f"No video file found for video ID {video_id}")
            return
        
        video_path = video.video_file.path
        
        if not os.path.exists(video_path):
            logger.error(f"Video file does not exist: {video_path}")
            return
        
        logger.info(f"Starting video processing for video ID {video_id}")
        
        # Update video duration
        duration = get_video_duration(video_path)
        if duration > 0:
            from datetime import timedelta
            video.duration = timedelta(seconds=duration)
            video.save()
        
        # Generate thumbnail if not exists
        if not video.thumbnail:
            thumbnail_filename = f"thumb_{video.id}.jpg"
            thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', thumbnail_filename)
            
            if extract_thumbnail(video_path, thumbnail_path):
                with open(thumbnail_path, 'rb') as thumb_file:
                    video.thumbnail.save(
                        thumbnail_filename,
                        ContentFile(thumb_file.read()),
                        save=False
                    )
        
        # Convert to different qualities
        qualities = ['480p', '720p', '1080p']
        
        for quality in qualities:
            # Check if quality already exists
            if not video.video_qualities.filter(quality=quality).exists():
                output_filename = f"{video.id}_{quality}.mp4"
                output_path = os.path.join(settings.MEDIA_ROOT, 'videos', 'converted', output_filename)
                
                if convert_video_quality(video_path, output_path, quality):
                    # Create VideoQuality record
                    VideoQuality.objects.create(
                        video=video,
                        quality=quality,
                        file_size=get_file_size(output_path),
                        video_file=f'videos/converted/{output_filename}'
                    )
                    logger.info(f"Created {quality} quality for video {video_id}")
                else:
                    logger.error(f"Failed to convert {quality} for video {video_id}")
        
        # Update processing status
        video.is_processed = True
        video.save()
        
        logger.info(f"Video processing completed for video ID {video_id}")
        
    except Video.DoesNotExist:
        logger.error(f"Video with ID {video_id} does not exist")
    except Exception as e:
        logger.error(f"Error processing video {video_id}: {e}")
