"""
URL configuration for Meu_proj_Django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.core.cache import cache
from django.http import HttpResponse
from spotify_app import views

def clear_all_cache(request):
    cache.clear()
    return HttpResponse("Cache limpo com sucesso!")

urlpatterns = [
    path('', views.spotify_login, name='home'),
    path('admin/', admin.site.urls),
    path('spotify/login/', views.spotify_login, name='login'),
    path('spotify/login-new/', views.login_new_account, name='login_new_account'),
    path('spotify/callback/', views.callback, name='callback'),
    path('spotify/rewind/', views.rewind, name='rewind'),
    path('profile/', views.profile, name='profile'),
    path('spotify/search/', views.search_track, name='search_track'),
    path('spotify/clear-cache/', views.clear_user_cache, name='clear_cache'),
    path('spotify/logout/', views.logout, name='logout'),
    path('clear-all-cache/', clear_all_cache, name='clear_all_cache'),
]
