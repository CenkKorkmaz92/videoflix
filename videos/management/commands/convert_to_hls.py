import os
import subprocess
import logging
from django.conf import settings
from django.core.management.base import BaseCommand
from videos.models import Video

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Convert videos to HLS format using FFmpeg'

    def add_arguments(self, parser):
        parser.add_argument('--video-id', type=int, help='Process specific video by ID')
        parser.add_argument('--all', action='store_true', help='Process all unprocessed videos')
        parser.add_argument('--force', action='store_true', help='Force reprocessing of already processed videos')

    def handle(self, *args, **options):
        if options['video_id']:
            try:
                video = Video.objects.get(id=options['video_id'])
                self.process_video(video, options['force'])
            except Video.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Video with ID {options["video_id"]} not found'))
        elif options['all']:
            if options['force']:
                videos = Video.objects.all()
            else:
                videos = Video.objects.filter(is_processed=False)
            
            self.stdout.write(f'Processing {videos.count()} videos...')
            for video in videos:
                self.process_video(video, options['force'])
        else:
            self.stdout.write(self.style.ERROR('Please specify --video-id or --all'))

    def process_video(self, video, force=False):
        """Process a single video to HLS format using mentor's FFmpeg command."""
        if video.is_processed and not force:
            self.stdout.write(f'Video "{video.title}" already processed. Use --force to reprocess.')
            return

        if not video.video_file:
            self.stdout.write(self.style.ERROR(f'No video file found for "{video.title}"'))
            return

        try:
            input_path = video.video_file.path
            
            hls_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(video.id))
            os.makedirs(hls_dir, exist_ok=True)
            
            output_m3u8 = os.path.join(hls_dir, 'index.m3u8')
            
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
            
            if force:
                cmd.insert(1, '-y')
            
            self.stdout.write(f'Processing video: {video.title}')
            self.stdout.write(f'Command: {" ".join(cmd)}')
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                video.is_processed = True
                video.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully converted "{video.title}" to HLS format')
                )
                self.stdout.write(f'HLS files saved to: {hls_dir}')
            else:
                self.stdout.write(
                    self.style.ERROR(f'FFmpeg failed for "{video.title}": {result.stderr}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error processing video "{video.title}": {str(e)}')
            )

    def get_hls_path(self, video_id):
        """Get the HLS directory path for a video."""
        return os.path.join(settings.MEDIA_ROOT, 'hls', str(video_id))
    
    def get_m3u8_path(self, video_id):
        """Get the m3u8 file path for a video."""
        return os.path.join(self.get_hls_path(video_id), 'index.m3u8')
