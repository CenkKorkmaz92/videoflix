from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Create placeholder thumbnail images for videos'

    def handle(self, *args, **options):
        # Create static/images directory if it doesn't exist
        static_images_dir = os.path.join(settings.BASE_DIR, 'staticfiles', 'images')
        os.makedirs(static_images_dir, exist_ok=True)
        
        # Create a simple placeholder image
        img = Image.new('RGB', (300, 200), color='#2c3e50')
        draw = ImageDraw.Draw(img)
        
        # Add text
        try:
            # Try to use a basic font
            font = ImageFont.load_default()
        except:
            font = None
            
        text = "Video Placeholder"
        if font:
            # Get text size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Center the text
            x = (300 - text_width) // 2
            y = (200 - text_height) // 2
            
            draw.text((x, y), text, fill='white', font=font)
        
        # Save the image
        placeholder_path = os.path.join(static_images_dir, 'video-placeholder.png')
        img.save(placeholder_path)
        
        self.stdout.write(
            self.style.SUCCESS(f'Created placeholder image at {placeholder_path}')
        )
        
        # Create multiple placeholder images for different videos (if any exist)
        try:
            from videos.models import Video
            videos = Video.objects.all()
            
            for video in videos:
                # Create unique placeholder for each video
                img = Image.new('RGB', (300, 200), color='#34495e')
                draw = ImageDraw.Draw(img)
                
                # Add video title
                title_text = video.title[:20] + "..." if len(video.title) > 20 else video.title
                
                if font:
                    # Get text size
                    bbox = draw.textbbox((0, 0), title_text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    # Center the text
                    x = (300 - text_width) // 2
                    y = (200 - text_height) // 2
                    
                    draw.text((x, y), title_text, fill='white', font=font)
                
                # Save video-specific placeholder
                video_placeholder_path = os.path.join(static_images_dir, f'video-{video.id}-placeholder.png')
                img.save(video_placeholder_path)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created placeholder for "{video.title}" at {video_placeholder_path}')
                )
        except Exception as e:
            # If no videos exist or other error, just continue with default placeholder
            self.stdout.write(
                self.style.WARNING(f'Could not create video-specific placeholders: {e}')
            )
