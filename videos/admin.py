
from django.contrib import admin
from django.contrib import messages
from django_rq import get_queue
from .models import Video, Genre
from .utils import process_video_task


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)


@admin.action(description="Mark selected videos as processed")
def mark_as_processed(modeladmin, request, queryset):
    """Mark selected videos as processed."""
    updated = queryset.update(is_processed=True)
    messages.success(request, f'{updated} videos marked as processed.')


@admin.action(description="Queue video processing")
def queue_video_processing(modeladmin, request, queryset):
    """Queue video processing for selected videos."""
    queue = get_queue('default')
    count = 0
    
    for video in queryset:
        if video.video_file:
            queue.enqueue(process_video_task, video.id)
            count += 1
    
    messages.success(request, f'{count} videos queued for processing.')


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_by", "created_at", "is_processed")
    list_editable = ("is_processed",)
    list_filter = ("is_processed", "genre", "created_at")
    search_fields = ("title", "uploaded_by__email")
    ordering = ("-created_at",)
    fields = ("title", "description", "genre", "video_file", "thumbnail", "is_processed", "uploaded_by")
    readonly_fields = ("uploaded_by",)
    actions = [mark_as_processed, queue_video_processing]
