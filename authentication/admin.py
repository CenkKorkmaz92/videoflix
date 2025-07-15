from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_staff", "is_superuser", "is_active", "is_email_verified", "date_joined", "last_login")
    search_fields = ("email",)
    ordering = ("email",)
