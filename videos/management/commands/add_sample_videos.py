from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from videos.models import Video, Genre
import os
import urllib.request


class Command(BaseCommand):
    help = 'Add sample videos to the database for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing videos before adding new ones',
        )
        parser.add_argument(
            '--download',
            action='store_true',
            help='Download sample videos from the internet',
        )

    def handle(self, *args, **options):
        if options['clear']:
            Video.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing videos'))

        # Ensure genres exist
        genres_data = [
            {'name': 'Action', 'slug': 'action'},
            {'name': 'Comedy', 'slug': 'comedy'},
            {'name': 'Drama', 'slug': 'drama'},
            {'name': 'Horror', 'slug': 'horror'},
            {'name': 'Sci-Fi', 'slug': 'sci-fi'},
        ]

        for genre_data in genres_data:
            genre, created = Genre.objects.get_or_create(
                name=genre_data['name'],
                defaults={'slug': genre_data['slug']}
            )
            if created:
                self.stdout.write(f'Created genre: {genre.name}')

        # Sample videos data
        sample_videos = [
            {
                'title': 'Big Buck Bunny',
                'description': 'A short computer-animated comedy film featuring a giant rabbit and his animal friends.',
                'genre': 'Comedy',
                'duration': '00:09:56',
                'video_url': 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4' if options['download'] else None
            },
            {
                'title': 'Elephant Dream',
                'description': 'A surreal short film about two characters exploring a strange world.',
                'genre': 'Sci-Fi',
                'duration': '00:10:53',
                'video_url': 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4' if options['download'] else None
            },
            {
                'title': 'Sintel',
                'description': 'A fantasy adventure about a girl searching for her lost dragon companion.',
                'genre': 'Drama',
                'duration': '00:14:48',
                'video_url': 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4' if options['download'] else None
            },
            {
                'title': 'Tears of Steel',
                'description': 'A sci-fi short film with impressive visual effects.',
                'genre': 'Action',
                'duration': '00:12:14',
                'video_url': 'http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4' if options['download'] else None
            }
        ]

        created_count = 0
        for video_data in sample_videos:
            genre = Genre.objects.get(name=video_data['genre'])
            
            # Check if video already exists
            if Video.objects.filter(title=video_data['title']).exists():
                self.stdout.write(f'Video "{video_data["title"]}" already exists, skipping...')
                continue

            video = Video(
                title=video_data['title'],
                description=video_data['description'],
                genre=genre,
                duration=video_data['duration']
            )

            if options['download'] and video_data['video_url']:
                try:
                    self.stdout.write(f'Downloading {video_data["title"]}...')
                    # Download the video file
                    response = urllib.request.urlopen(video_data['video_url'])
                    video_content = response.read()
                    
                    # Create a file name
                    file_name = f"{video_data['title'].lower().replace(' ', '_')}.mp4"
                    
                    # Save the video file
                    video.video_file.save(
                        file_name,
                        ContentFile(video_content),
                        save=False
                    )
                    self.stdout.write(self.style.SUCCESS(f'Downloaded and saved {video_data["title"]}'))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'Failed to download {video_data["title"]}: {str(e)}'))

            video.save()
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'Created video: {video.title}'))

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample videos')
        )
        
        if not options['download']:
            self.stdout.write(
                self.style.WARNING(
                    'Videos were created without files. Use --download to download sample video files, '
                    'or manually upload videos through the admin interface or API.'
                )
            )
