from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.spotify_login, name='login'),
    path('callback/', views.callback, name='callback'),
    path('rewind/', views.rewind, name='rewind'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout, name='logout'),
    path('test/', views.test_view, name='test'),
    
    # Novas páginas de usuário
    path('login-alt/', views.login_alt, name='login_alt'),
    path('register/', views.register_user, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('settings/', views.user_settings, name='settings'),
]





