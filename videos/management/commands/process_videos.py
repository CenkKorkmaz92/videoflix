from django.core.management.base import BaseCommand
from videos.models import Video
from videos.tasks import create_video_qualities


class Command(BaseCommand):
    help = 'Process video qualities for uploaded videos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--video_id',
            type=int,
            help='Process specific video by ID',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Process all unprocessed videos',
        )

    def handle(self, *args, **options):
        if options['video_id']:
            try:
                video = Video.objects.get(id=options['video_id'])
                self.stdout.write(f'Processing video {video.id}: {video.title}')
                create_video_qualities(video.id)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully processed video {video.id}')
                )
            except Video.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Video with ID {options["video_id"]} not found')
                )
        elif options['all']:
            unprocessed_videos = Video.objects.filter(is_processed=False)
            self.stdout.write(f'Found {unprocessed_videos.count()} unprocessed videos')
            
            for video in unprocessed_videos:
                self.stdout.write(f'Processing video {video.id}: {video.title}')
                try:
                    create_video_qualities(video.id)
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully processed video {video.id}')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error processing video {video.id}: {e}')
                    )
        else:
            self.stdout.write(
                self.style.ERROR('Please specify --video_id or --all')
            )
