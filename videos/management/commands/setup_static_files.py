from django.core.management.base import BaseCommand
from django.core.management import call_command
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Setup static files and placeholder images for VideoFlix'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Setting up VideoFlix static files...')
        )
        
        self.stdout.write('📁 Collecting static files...')
        call_command('collectstatic', '--noinput')
        
        self.stdout.write('🖼️ Creating placeholder images...')
        call_command('create_placeholders')
        
        static_images_dir = os.path.join(settings.STATIC_ROOT, 'images')
        placeholder_path = os.path.join(static_images_dir, 'video-placeholder.png')
        
        if os.path.exists(placeholder_path):
            self.stdout.write(
                self.style.SUCCESS('✅ VideoFlix static files setup complete!')
            )
            self.stdout.write(
                f'📍 Placeholder images available at: {static_images_dir}'
            )
        else:
            self.stdout.write(
                self.style.ERROR('❌ Setup incomplete - placeholder images missing')
            )
        
        self.stdout.write(
            self.style.SUCCESS('🎬 VideoFlix is ready for video uploads!')
        )
