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
    
    def list(self, request, *args, **kwargs):
        """Return videos as direct array for frontend compatibility."""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        # Return direct array instead of {"results": [...]} or {"videos": [...]}
        return Response(serializer.data)


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
    
    # Development fallback: create resolution-specific manifest
    if video.video_file:
        # Get resolution-specific video URL if available
        video_url = None
        
        # Try to find VideoQuality for this resolution
        try:
            from ..models import VideoQuality
            quality_obj = VideoQuality.objects.get(video=video, quality=resolution)
            if quality_obj.video_file:
                video_url = request.build_absolute_uri(quality_obj.video_file.url)
        except VideoQuality.DoesNotExist:
            pass
        
        # Fallback to original video file
        if not video_url:
            video_url = request.build_absolute_uri(video.video_file.url)
        
        # Create a simple single-segment manifest
        manifest_content = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:3600
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-PLAYLIST-TYPE:VOD
#EXTINF:3600.0,
{video_url}
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


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def processing_status(request):
    """
    Get processing status of all videos for debugging.
    Only accessible by admin users.
    """
    from django.utils import timezone
    import os
    
    # Get all videos with processing status
    videos = Video.objects.all().order_by('-created_at')
    
    status_data = []
    for video in videos:
        video_data = {
            'id': video.id,
            'title': video.title,
            'is_processed': video.is_processed,
            'created_at': video.created_at,
            'has_video_file': bool(video.video_file),
            'file_exists': False,
            'file_size': 0,
            'processing_age_hours': (timezone.now() - video.created_at).total_seconds() / 3600
        }
        
        if video.video_file:
            try:
                if os.path.exists(video.video_file.path):
                    video_data['file_exists'] = True
                    video_data['file_size'] = os.path.getsize(video.video_file.path)
            except Exception:
                pass
        
        status_data.append(video_data)
    
    # Summary statistics
    total_videos = len(status_data)
    processed_videos = len([v for v in status_data if v['is_processed']])
    unprocessed_videos = total_videos - processed_videos
    
    return Response({
        'summary': {
            'total_videos': total_videos,
            'processed_videos': processed_videos,
            'unprocessed_videos': unprocessed_videos
        },
        'videos': status_data
    })


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def force_process_video(request, video_id):
    """
    Force processing of a specific video.
    Only accessible by admin users.
    """
    from django_rq import get_queue
    from ..utils import process_video_task
    
    try:
        video = Video.objects.get(id=video_id)
        
        if not video.video_file:
            return Response({
                'error': 'Video has no file to process'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Queue the video for processing
        queue = get_queue('default')
        job = queue.enqueue(process_video_task, video.id)
        
        return Response({
            'detail': f'Video {video_id} queued for processing',
            'job_id': job.id,
            'video_title': video.title
        })
        
    except Video.DoesNotExist:
        return Response({
            'error': 'Video not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def mark_video_processed(request, video_id):
    """
    Manually mark a video as processed without actual processing.
    Only accessible by admin users.
    """
    try:
        video = Video.objects.get(id=video_id)
        video.is_processed = True
        video.save()
        
        return Response({
            'detail': f'Video {video_id} marked as processed',
            'video_title': video.title
        })
        
    except Video.DoesNotExist:
        return Response({
            'error': 'Video not found'
        }, status=status.HTTP_404_NOT_FOUND)
