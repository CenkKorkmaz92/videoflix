from rest_framework import generics, permissions
from .models import ContentPage
from .serializers import ContentPageSerializer


class ContentPageListView(generics.ListAPIView):
    """
    Get list of all active content pages.
    """
    queryset = ContentPage.objects.filter(is_active=True)
    serializer_class = ContentPageSerializer
    permission_classes = [permissions.AllowAny]


class ContentPageDetailView(generics.RetrieveAPIView):
    """
    Get content page by slug.
    """
    queryset = ContentPage.objects.filter(is_active=True)
    serializer_class = ContentPageSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
