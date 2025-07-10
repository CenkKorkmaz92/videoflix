from rest_framework import serializers
from ..models import ContentPage


class ContentPageSerializer(serializers.ModelSerializer):
    """
    Serializer for content pages.
    """
    class Meta:
        model = ContentPage
        fields = ['id', 'title', 'slug', 'content', 'updated_at']
