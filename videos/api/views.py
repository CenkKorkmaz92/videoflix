from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_rq import get_queue
from ..models import Video, Genre, WatchProgress
from .serializers import (
    VideoListSerializer, VideoDetailSerializer, VideoUploadSerializer,
    WatchProgressSerializer, GenreSerializer, DashboardSerializer
)
from ..utils import process_video_task


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


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Allow unauthenticated access for development
def hls_manifest(request, movie_id, resolution):
    """
    Serve HLS manifest file for video streaming.
    Uses mentor's FFmpeg HLS conversion approach.
    """
    from django.http import HttpResponse, Http404
    from ..hls_utils import hls_processor
    
    try:
        video = Video.objects.get(id=movie_id, is_processed=True)
    except Video.DoesNotExist:
        raise Http404("Video not found")
    
    # Check if HLS files exist (from mentor's FFmpeg conversion)
    if hls_processor.hls_exists(video.id):
        try:
            manifest_path = hls_processor.get_m3u8_path(video.id)
            with open(manifest_path, 'r') as f:
                content = f.read()
            
            response = HttpResponse(content, content_type='application/vnd.apple.mpegurl')
            response['Cache-Control'] = 'no-cache'
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
            
        except Exception:
            raise Http404("Error reading HLS manifest")
    
    # Development fallback: create a simple manifest pointing to MP4
    if video.video_file:
        # For development, create a simpler HLS manifest that should work with HLS.js
        mp4_url = request.build_absolute_uri(video.video_file.url)
        
        # Get video duration and create segments
        total_seconds = 600  # Default 10 minutes
        if hasattr(video, 'duration') and video.duration:
            if hasattr(video.duration, 'total_seconds'):
                total_seconds = int(video.duration.total_seconds())
            else:
                # Parse duration string like "0:12:14"
                time_parts = str(video.duration).split(':')
                if len(time_parts) == 3:
                    hours, minutes, seconds = map(int, time_parts)
                    total_seconds = hours * 3600 + minutes * 60 + seconds
        
        # Create segments of 10 seconds each for better HLS.js compatibility
        segment_duration = 10
        segments = []
        current_time = 0
        
        while current_time < total_seconds:
            remaining = total_seconds - current_time
            seg_duration = min(segment_duration, remaining)
            segments.append(f"#EXTINF:{seg_duration:.1f},\n{mp4_url}")
            current_time += seg_duration
        
        # If no segments were created, create at least one
        if not segments:
            segments = [f"#EXTINF:{total_seconds:.1f},\n{mp4_url}"]
        
        manifest_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:{segment_duration}
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-PLAYLIST-TYPE:VOD
{chr(10).join(segments)}
#EXT-X-ENDLIST
"""
        
        response = HttpResponse(manifest_content, content_type='application/vnd.apple.mpegurl')
        response['Cache-Control'] = 'no-cache'
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
    
    raise Http404("Video file not found")


@api_view(['GET'])
@permission_classes([permissions.AllowAny])  # Allow unauthenticated access for development
def hls_segment(request, movie_id, resolution, segment):
    """
    Serve HLS video segments for streaming.
    Uses segments created by mentor's FFmpeg conversion.
    """
    from django.http import HttpResponse, Http404
    import os
    from ..hls_utils import hls_processor
    
    try:
        video = Video.objects.get(id=movie_id, is_processed=True)
    except Video.DoesNotExist:
        raise Http404("Video not found")
    
    # Build path to segment file using HLS processor
    segment_path = os.path.join(hls_processor.get_hls_directory(video.id), segment)
    
    if not os.path.exists(segment_path):
        raise Http404("Segment not found")
    
    try:
        with open(segment_path, 'rb') as f:
            content = f.read()
        
        response = HttpResponse(content, content_type='video/MP2T')
        response['Cache-Control'] = 'max-age=3600'  # Cache segments for 1 hour
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        return response
        
    except Exception:
        raise Http404("Error reading segment")
