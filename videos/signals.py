from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import SuspiciousFileOperation
import os
from .models import Video


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for when a video is saved.
    Automatically starts video processing for new uploads.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🎬 SIGNAL TRIGGERED: Video {instance.id} saved, created={created}")
    print(f"🎬 SIGNAL TRIGGERED: Video {instance.id} saved, created={created}")
    
    if created and instance.video_file:
        logger.info(f"🚀 Starting background processing for video {instance.id}")
        print(f"🚀 Starting background processing for video {instance.id}")
        # Process video in background using RQ queue
        try:
            from django_rq import get_queue
            from .tasks import create_video_qualities
            
            queue = get_queue('default')
            job = queue.enqueue(create_video_qualities, instance.id)
            logger.info(f"✅ Job queued: {job.id}")
            print(f"✅ Job queued: {job.id}")
        except Exception as e:
            logger.error(f"❌ Error queuing job: {e}")
            print(f"❌ Error queuing job: {e}")
            # Fallback to direct processing if RQ fails
            from .tasks import create_video_qualities
            create_video_qualities(instance.id)
    else:
        logger.info(f"⏭️ Skipping processing: created={created}, has_file={bool(instance.video_file)}")
        print(f"⏭️ Skipping processing: created={created}, has_file={bool(instance.video_file)}")


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    """
    Signal handler for when a video is deleted.
    Cleans up associated files from filesystem.
    """
    # Delete video file
    if instance.video_file and os.path.isfile(instance.video_file.path):
        try:
            os.remove(instance.video_file.path)
        except OSError:
            pass
    
    # Delete thumbnail file
    if instance.thumbnail:
        try:
            thumbnail_path = instance.thumbnail.path
            if os.path.isfile(thumbnail_path):
                os.remove(thumbnail_path)
        except (OSError, ValueError, SuspiciousFileOperation):
            # Handle cases where file doesn't exist or path is outside media root
            pass
    
    # Delete processed video files
    for quality in instance.qualities.all():
        if quality.file_path and os.path.isfile(quality.file_path):
            try:
                os.remove(quality.file_path)
            except OSError:
                pass
