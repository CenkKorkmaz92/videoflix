from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "is_staff", "is_superuser", "is_active", "is_email_verified", "date_joined", "last_login")
    list_filter = ("is_active", "is_email_verified")
    search_fields = ("email",)
    ordering = ("email",)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'is_email_verified' in form.base_fields:
            form.base_fields['is_email_verified'].help_text = (
                'Indicates whether the user has verified their email address. '
                'Use "is_active" to enable/disable login access.'
            )
        return form
