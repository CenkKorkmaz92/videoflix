"""
HLS (HTTP Live Streaming) utilities for video processing.
Uses FFmpeg with mentor-provided command for HLS conversion.
"""

import os
import subprocess
import logging
from django.conf import settings
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)


class HLSProcessor:
    """
    HLS video processor using FFmpeg with mentor's specifications.
    """
    
    def __init__(self):
        self.hls_base_path = os.path.join(settings.MEDIA_ROOT, 'hls')
        os.makedirs(self.hls_base_path, exist_ok=True)
    
    def convert_to_hls(self, video_instance, force=False):
        """
        Convert video to HLS format using mentor's FFmpeg command:
        ffmpeg -i input.mp4 -codec: copy -start_number 0 -hls_time 10 -hls_list_size 0 -f hls output.m3u8
        """
        if video_instance.is_processed and not force:
            logger.info(f'Video {video_instance.id} already processed')
            return True
        
        if not video_instance.video_file:
            logger.error(f'No video file found for video {video_instance.id}')
            return False
        
        try:
            # Input file path
            input_path = video_instance.video_file.path
            
            # Create HLS directory for this video
            hls_dir = os.path.join(self.hls_base_path, str(video_instance.id))
            os.makedirs(hls_dir, exist_ok=True)
            
            # Output m3u8 file
            output_m3u8 = os.path.join(hls_dir, 'index.m3u8')
            
            # Mentor's FFmpeg command
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-codec:', 'copy',
                '-start_number', '0',
                '-hls_time', '10',
                '-hls_list_size', '0',
                '-f', 'hls',
                output_m3u8
            ]
            
            # Add overwrite flag if force is True
            if force:
                cmd.insert(1, '-y')
            
            logger.info(f'Converting video {video_instance.id} to HLS')
            logger.debug(f'FFmpeg command: {" ".join(cmd)}')
            
            # Execute FFmpeg
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                # Mark as processed
                video_instance.is_processed = True
                video_instance.save()
                
                logger.info(f'Successfully converted video {video_instance.id} to HLS')
                return True
            else:
                logger.error(f'FFmpeg failed for video {video_instance.id}: {result.stderr}')
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f'FFmpeg timeout for video {video_instance.id}')
            return False
        except Exception as e:
            logger.error(f'Error converting video {video_instance.id} to HLS: {str(e)}')
            return False
    
    def get_hls_directory(self, video_id):
        """Get HLS directory path for a video."""
        return os.path.join(self.hls_base_path, str(video_id))
    
    def get_m3u8_path(self, video_id):
        """Get m3u8 file path for a video."""
        return os.path.join(self.get_hls_directory(video_id), 'index.m3u8')
    
    def get_m3u8_url(self, video_id):
        """Get m3u8 file URL for a video."""
        return f'{settings.MEDIA_URL}hls/{video_id}/index.m3u8'
    
    def hls_exists(self, video_id):
        """Check if HLS files exist for a video."""
        m3u8_path = self.get_m3u8_path(video_id)
        return os.path.exists(m3u8_path)
    
    def get_hls_segments(self, video_id):
        """Get list of HLS segment files for a video."""
        hls_dir = self.get_hls_directory(video_id)
        if not os.path.exists(hls_dir):
            return []
        
        segments = []
        for filename in os.listdir(hls_dir):
            if filename.endswith('.ts'):
                segments.append(filename)
        
        return sorted(segments)
    
    def cleanup_hls_files(self, video_id):
        """Remove HLS files for a video."""
        hls_dir = self.get_hls_directory(video_id)
        if os.path.exists(hls_dir):
            import shutil
            shutil.rmtree(hls_dir)
            logger.info(f'Cleaned up HLS files for video {video_id}')


# Global instance
hls_processor = HLSProcessor()
