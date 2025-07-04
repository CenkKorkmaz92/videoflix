from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('password-reset/request/', views.request_password_reset, name='password_reset_request'),
    path('password-reset/<str:token>/', views.reset_password, name='password_reset'),
    path('profile/', views.get_user_profile, name='profile'),
]
