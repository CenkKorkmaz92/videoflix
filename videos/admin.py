from django.contrib import admin
from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "created_at", "is_processed")
    search_fields = ("title", "owner__email")
    ordering = ("-created_at",)
