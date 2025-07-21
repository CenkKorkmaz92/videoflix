from django.core.management.base import BaseCommand
from django.utils import timezone
from django_rq import get_queue
from videos.models import Video
from videos.utils import process_video_task
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Process pending videos that are not yet processed'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mark-all-processed',
            action='store_true',
            help='Mark all videos as processed without actual processing'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Only process videos created in the last N days (default: 30)'
        )
        parser.add_argument(
            '--queue-only',
            action='store_true',
            help='Only queue videos for processing, do not mark as processed'
        )

    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timezone.timedelta(days=options['days'])
        unprocessed_videos = Video.objects.filter(
            is_processed=False,
            created_at__gte=cutoff_date
        )

        self.stdout.write(f"Found {unprocessed_videos.count()} unprocessed videos")

        if options['mark_all_processed']:
            updated = unprocessed_videos.update(is_processed=True)
            self.stdout.write(
                self.style.SUCCESS(f'Marked {updated} videos as processed')
            )
            return

        if options['queue_only']:
            queue = get_queue('default')
            count = 0
            
            for video in unprocessed_videos:
                if video.video_file:
                    queue.enqueue(process_video_task, video.id)
                    count += 1
                    self.stdout.write(f"Queued video: {video.title}")
            
            self.stdout.write(
                self.style.SUCCESS(f'Queued {count} videos for processing')
            )
            return

        for video in unprocessed_videos:
            self.stdout.write(f"\nVideo ID: {video.id}")
            self.stdout.write(f"Title: {video.title}")
            self.stdout.write(f"Created: {video.created_at}")
            self.stdout.write(f"Has video file: {bool(video.video_file)}")
            
            if video.video_file:
                try:
                    import os
                    file_exists = os.path.exists(video.video_file.path)
                    self.stdout.write(f"File exists: {file_exists}")
                    if file_exists:
                        file_size = os.path.getsize(video.video_file.path)
                        self.stdout.write(f"File size: {file_size} bytes")
                except Exception as e:
                    self.stdout.write(f"Error checking file: {e}")

        self.stdout.write(
            self.style.WARNING(
                f'\nTo fix these videos, you can:\n'
                f'1. Run: python manage.py process_pending_videos --queue-only\n'
                f'2. Run: python manage.py process_pending_videos --mark-all-processed\n'
                f'3. Use the admin interface to manually mark videos as processed'
            )
        )
