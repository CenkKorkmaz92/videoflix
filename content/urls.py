from django.urls import path
from .api import views

app_name = 'content'

urlpatterns = [
    path('', views.ContentPageListView.as_view(), name='page-list'),
    path('<slug:slug>/', views.ContentPageDetailView.as_view(), name='page-detail'),
]
