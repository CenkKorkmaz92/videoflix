from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_rq import get_queue
from .models import Video, Genre, WatchProgress
from .serializers import (
    VideoListSerializer, VideoDetailSerializer, VideoUploadSerializer,
    WatchProgressSerializer, GenreSerializer, DashboardSerializer
)
from .utils import process_video_task


class GenreListView(generics.ListAPIView):
    """
    Get list of all genres.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.AllowAny]


class VideoListView(generics.ListAPIView):
    """
    Get list of videos with filtering and search.
    """
    serializer_class = VideoListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Filter videos by genre and search query."""
        queryset = Video.objects.filter(is_processed=True)
        
        # Filter by genre
        genre = self.request.query_params.get('genre')
        if genre:
            queryset = queryset.filter(genre__slug=genre)
        
        # Search by title or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')


class VideoDetailView(generics.RetrieveAPIView):
    """
    Get video details.
    """
    queryset = Video.objects.filter(is_processed=True)
    serializer_class = VideoDetailSerializer
    permission_classes = [permissions.AllowAny]


class VideoUploadView(generics.CreateAPIView):
    """
    Upload a new video.
    """
    serializer_class = VideoUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Save video and start processing."""
        video = serializer.save(uploaded_by=self.request.user)
        
        # Queue video processing task
        queue = get_queue('default')
        queue.enqueue(process_video_task, video.id)


class WatchProgressView(generics.CreateAPIView, generics.UpdateAPIView):
    """
    Update watch progress for a video.
    """
    serializer_class = WatchProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create watch progress for user and video."""
        video_id = self.kwargs.get('video_id')
        video = get_object_or_404(Video, id=video_id, is_processed=True)
        
        progress, created = WatchProgress.objects.get_or_create(
            user=self.request.user,
            video=video
        )
        return progress
    
    def post(self, request, *args, **kwargs):
        """Create or update watch progress."""
        return self.update(request, *args, **kwargs)
    
    def put(self, request, *args, **kwargs):
        """Update watch progress."""
        return self.update(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_watch_progress(request):
    """
    Get user's watch progress for all videos.
    """
    progress_list = WatchProgress.objects.filter(
        user=request.user
    ).select_related('video')
    
    serializer = WatchProgressSerializer(progress_list, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def dashboard_data(request):
    """
    Get dashboard data including hero video and genre-based videos.
    """
    # Get hero video (most recent processed video)
    hero_video = Video.objects.filter(is_processed=True).order_by('-created_at').first()
    
    data = {'hero_video': hero_video}
    serializer = DashboardSerializer(data, context={'user': request.user})
    
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_video(request, video_id):
    """
    Delete a video (only by uploader or admin).
    """
    video = get_object_or_404(Video, id=video_id)
    
    # Check permissions
    if video.uploaded_by != request.user and not request.user.is_staff:
        return Response(
            {'detail': 'You do not have permission to delete this video.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    video.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
