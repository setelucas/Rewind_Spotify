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
from spotify_app import views

urlpatterns = [
    path('', views.spotify_login, name='home'),  # Adicione esta linha para a página inicial
    path('admin/', admin.site.urls),
    path('spotify/login/', views.spotify_login, name='login'),
    path('spotify/callback/', views.callback, name='callback'),
    path('spotify/rewind/', views.rewind, name='rewind'),
    path('profile/', views.profile, name='profile'),
    path('spotify/search/', views.search_track, name='search_track'),  # Nova URL para busca de músicas
]
