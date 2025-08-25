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
    
    # APIs para edição
    path('update-bio/', views.update_bio, name='update_bio'),
    path('update-rewind-title/', views.update_rewind_title, name='update_rewind_title'),
    path('update-rewind-items/', views.update_rewind_items, name='update_rewind_items'),
    path('api/search-tracks/', views.search_tracks, name='search_tracks'),
    
    # Novas páginas de usuário
    path('login-alt/', views.login_alt, name='login_alt'),
    path('register/', views.register_user, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('settings/', views.user_settings, name='settings'),
]


