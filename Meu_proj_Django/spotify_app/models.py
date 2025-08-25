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
    
    # Campos editáveis pelo usuário
    bio = models.TextField(max_length=500, blank=True, default="Apaixonado por música, sempre descobrindo novos sons e compartilhando as melhores playlists.")
    custom_rewind_title = models.CharField(max_length=100, blank=True, default="Meu Rewind Musical")
    
    def __str__(self):
        return self.display_name or self.spotify_id

    def is_token_expired(self):
        return self.token_expires_at <= timezone.now()

class CustomRewindItem(models.Model):
    """
    Modelo para itens personalizados do rewind do usuário
    """
    user = models.ForeignKey(SpotifyUser, on_delete=models.CASCADE, related_name='custom_rewind_items')
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    album = models.CharField(max_length=200, blank=True, null=True)
    duration = models.CharField(max_length=10, blank=True, null=True)  # formato "3:45"
    popularity = models.IntegerField(blank=True, null=True)
    description = models.TextField(max_length=300, blank=True)
    position = models.PositiveSmallIntegerField()
    image = models.URLField(max_length=500, blank=True, null=True)
    spotify_url = models.URLField(max_length=500, blank=True, null=True)
    
    class Meta:
        ordering = ['position']
    
    def __str__(self):
        return f"{self.position}º - {self.title} by {self.artist}"
