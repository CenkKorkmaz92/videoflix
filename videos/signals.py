from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_rq import get_queue
import os
from .models import Video
from .utils import process_video_task


@receiver(post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for when a video is saved.
    Automatically starts video processing for new uploads.
    """
    if created and instance.video_file:
        # Queue video processing task when a new video is created
        queue = get_queue('default')
        queue.enqueue(process_video_task, instance.id)


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
    if instance.thumbnail and os.path.isfile(instance.thumbnail.path):
        try:
            os.remove(instance.thumbnail.path)
        except OSError:
            pass
    
    # Delete processed video files
    for quality in instance.qualities.all():
        if quality.file_path and os.path.isfile(quality.file_path):
            try:
                os.remove(quality.file_path)
            except OSError:
                pass
