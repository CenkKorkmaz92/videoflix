from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from videos.models import Video
from videos.utils import extract_thumbnail
import os


class Command(BaseCommand):
    help = 'Generate actual video thumbnails from video frames for all processed videos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate thumbnails even if they already exist'
        )
        parser.add_argument(
            '--video-id',
            type=int,
            help='Generate thumbnail for specific video ID only'
        )

    def handle(self, *args, **options):
        if options['video_id']:
            try:
                video = Video.objects.get(id=options['video_id'], is_processed=True)
                videos = [video]
                self.stdout.write(f'Processing single video: {video.title}')
            except Video.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Video with ID {options["video_id"]} not found or not processed')
                )
                return
        else:
            videos = Video.objects.filter(is_processed=True)
            self.stdout.write(f'Processing {videos.count()} processed videos...')

        successful_count = 0
        failed_count = 0

        for video in videos:
            if video.thumbnail and not options['force']:
                self.stdout.write(f'Skipping {video.title} (thumbnail already exists)')
                continue

            if not video.video_file:
                self.stdout.write(
                    self.style.WARNING(f'No video file for: {video.title}')
                )
                failed_count += 1
                continue

            video_path = video.video_file.path
            
            if not os.path.exists(video_path):
                self.stdout.write(
                    self.style.WARNING(f'Video file not found: {video_path}')
                )
                failed_count += 1
                continue

            # Create thumbnail filename
            thumbnail_filename = f"thumb_{video.id}.jpg"
            thumbnail_path = os.path.join(
                settings.MEDIA_ROOT,
                'thumbnails',
                thumbnail_filename
            )
            
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            
            # Extract thumbnail at 2 seconds (or 10% of video duration)
            try:
                # Try to extract at 2 seconds first
                if extract_thumbnail(video_path, thumbnail_path, time_offset="00:00:02"):
                    # Save to video model
                    with open(thumbnail_path, 'rb') as thumb_file:
                        video.thumbnail.save(
                            thumbnail_filename,
                            ContentFile(thumb_file.read()),
                            save=True
                        )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Generated thumbnail for: {video.title}')
                    )
                    successful_count += 1
                else:
                    # Try at 1 second if 2 seconds fails
                    if extract_thumbnail(video_path, thumbnail_path, time_offset="00:00:01"):
                        with open(thumbnail_path, 'rb') as thumb_file:
                            video.thumbnail.save(
                                thumbnail_filename,
                                ContentFile(thumb_file.read()),
                                save=True
                            )
                        
                        self.stdout.write(
                            self.style.SUCCESS(f'Generated thumbnail for: {video.title} (at 1s)')
                        )
                        successful_count += 1
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'Failed to extract thumbnail for: {video.title}')
                        )
                        failed_count += 1
                        
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {video.title}: {str(e)}')
                )
                failed_count += 1

        # Summary
        self.stdout.write('')
        self.stdout.write(f'Thumbnail generation complete!')
        self.stdout.write(f'Successful: {successful_count}')
        self.stdout.write(f'Failed: {failed_count}')
        self.stdout.write(f'Total processed: {successful_count + failed_count}')
