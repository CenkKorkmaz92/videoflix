from django.core.management.base import BaseCommand
from videos.models import Genre

class Command(BaseCommand):
    help = 'Seed the database with default genres.'

    def handle(self, *args, **options):
        genres = [
            'Action',
            'Comedy',
            'Drama',
            'Documentary',
        ]
        created = 0
        for genre_name in genres:
            obj, was_created = Genre.objects.get_or_create(name=genre_name)
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created} genres.'))
