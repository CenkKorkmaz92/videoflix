from django.urls import path
from .api import views

app_name = 'videos'

urlpatterns = [
    path('video/', views.VideoListView.as_view(), name='video-list'),
    path('video/<int:movie_id>/<str:resolution>/index.m3u8', views.hls_manifest, name='hls-manifest'),
    path('videos/<int:movie_id>/<str:resolution>/index.m3u8', views.hls_manifest, name='hls-manifest-plural'),
    path('video/<int:movie_id>/<str:resolution>/<str:segment>', views.hls_segment, name='hls-segment'),
    path('videos/<int:movie_id>/<str:resolution>/<str:segment>', views.hls_segment, name='hls-segment-plural'),
    
    path('video/<int:pk>/', views.VideoDetailView.as_view(), name='video-detail'),
    path('video/upload/', views.VideoUploadView.as_view(), name='video-upload'),
    path('video/<int:video_id>/delete/', views.delete_video, name='video-delete'),
    
    path('genres/', views.GenreListView.as_view(), name='genre-list'),
    
    path('video/<int:video_id>/progress/', views.WatchProgressView.as_view(), name='watch-progress'),
    path('progress/', views.user_watch_progress, name='user-progress'),
    
    path('dashboard/', views.dashboard_data, name='dashboard'),
    
    path('admin/processing-status/', views.processing_status, name='processing-status'),
    path('admin/force-process/<int:video_id>/', views.force_process_video, name='force-process'),
    path('admin/mark-processed/<int:video_id>/', views.mark_video_processed, name='mark-processed'),
]
