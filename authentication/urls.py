from django.urls import path
from .api import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('activate/<str:uidb64>/<str:token>/', views.activate_account, name='activate'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('token/refresh/', views.refresh_token, name='token_refresh'),
    path('password_reset/', views.request_password_reset, name='password_reset'),
    path('password_confirm/<str:uidb64>/<str:token>/', views.confirm_password_reset, name='password_confirm'),
    path('test/get_reset_token/<str:uidb64>/', views.get_reset_token_for_testing, name='get_reset_token_test'),
]
