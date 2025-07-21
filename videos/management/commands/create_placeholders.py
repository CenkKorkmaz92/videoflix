from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Create placeholder thumbnail images for videos and generate real video thumbnails'

    def handle(self, *args, **options):
        # First create the generic fallback placeholder
        static_images_dir = os.path.join(settings.BASE_DIR, 'staticfiles', 'images')
        os.makedirs(static_images_dir, exist_ok=True)
        
        img = Image.new('RGB', (300, 200), color='gray')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
            
        text = "Video Placeholder"
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (300 - text_width) // 2
            y = (200 - text_height) // 2
            
            draw.text((x, y), text, fill='white', font=font)
        
        placeholder_path = os.path.join(static_images_dir, 'video-placeholder.png')
        img.save(placeholder_path)
        
        self.stdout.write(
            self.style.SUCCESS(f'Created placeholder image at {placeholder_path}')
        )
        
        # Generate real video thumbnails for processed videos
        try:
            from videos.models import Video
            from videos.utils import extract_thumbnail
            from django.core.files.base import ContentFile
            
            processed_videos = Video.objects.filter(is_processed=True)
            
            for video in processed_videos:
                if video.thumbnail:
                    self.stdout.write(f'Video "{video.title}" already has thumbnail, skipping')
                    continue
                
                if not video.video_file or not os.path.exists(video.video_file.path):
                    self.stdout.write(f'Video file not found for "{video.title}", creating text placeholder')
                    
                    # Create text-based placeholder for this video
                    img = Image.new('RGB', (300, 200), color='darkgray')
                    draw = ImageDraw.Draw(img)
                    
                    title_text = video.title[:20] + "..." if len(video.title) > 20 else video.title
                    
                    if font:
                        bbox = draw.textbbox((0, 0), title_text, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        
                        x = (300 - text_width) // 2
                        y = (200 - text_height) // 2
                        
                        draw.text((x, y), title_text, fill='white', font=font)
                    
                    video_placeholder_path = os.path.join(static_images_dir, f'video-{video.id}-placeholder.png')
                    img.save(video_placeholder_path)
                    
                    self.stdout.write(
                        self.style.WARNING(f'Created text placeholder for "{video.title}" at {video_placeholder_path}')
                    )
                    continue
                
                # Extract real video thumbnail
                thumbnail_filename = f"thumb_{video.id}.jpg"
                thumbnail_path = os.path.join(
                    settings.MEDIA_ROOT,
                    'thumbnails',
                    thumbnail_filename
                )
                
                os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
                
                if extract_thumbnail(video.video_file.path, thumbnail_path, time_offset="00:00:02"):
                    with open(thumbnail_path, 'rb') as thumb_file:
                        video.thumbnail.save(
                            thumbnail_filename,
                            ContentFile(thumb_file.read()),
                            save=True
                        )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'Generated video thumbnail for "{video.title}"')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Could not extract thumbnail for "{video.title}"')
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Error generating video thumbnails: {e}')
            )
