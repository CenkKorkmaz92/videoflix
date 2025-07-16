
from django.contrib import admin
from .models import Video, Genre


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_by", "created_at", "is_processed")
    search_fields = ("title", "uploaded_by__email")
    ordering = ("-created_at",)
