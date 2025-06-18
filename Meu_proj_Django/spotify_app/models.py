from django.db import models
from django.utils import timezone

class SpotifyUser(models.Model):
    """
    Modelo para armazenar informações do usuário Spotify.
    """
    spotify_id = models.CharField(max_length=100, primary_key=True)
    display_name = models.CharField(max_length=200, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    profile_image = models.URLField(null=True, blank=True)
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display_name or self.spotify_id
    
    def is_token_expired(self):
        """
        Verifica se o token está expirado.
        Retorna True se o token expira em menos de 60 segundos.
        """
        # Adicionar um buffer de 60 segundos para evitar problemas de timing
        return self.token_expires_at <= timezone.now() + timezone.timedelta(seconds=60)
