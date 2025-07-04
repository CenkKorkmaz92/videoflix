from django.urls import path
from . import views

app_name = 'videos'

urlpatterns = [
    # Genre endpoints
    path('genres/', views.GenreListView.as_view(), name='genre-list'),
    
    # Video endpoints
    path('', views.VideoListView.as_view(), name='video-list'),
    path('<int:pk>/', views.VideoDetailView.as_view(), name='video-detail'),
    path('upload/', views.VideoUploadView.as_view(), name='video-upload'),
    path('<int:video_id>/delete/', views.delete_video, name='video-delete'),
    
    # Watch progress endpoints
    path('<int:video_id>/progress/', views.WatchProgressView.as_view(), name='watch-progress'),
    path('progress/', views.user_watch_progress, name='user-progress'),
    
    # Dashboard
    path('dashboard/', views.dashboard_data, name='dashboard'),
]
