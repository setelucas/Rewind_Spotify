from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.conf import settings
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def spotify_login(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-top-read"
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def callback(request):
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-top-read"
    )
    code = request.GET.get('code')
    token_info = sp_oauth.get_access_token(code)
    access_token = token_info['access_token']
    
    # Salvar o token na sessão
    request.session['spotify_token'] = token_info
    
    # Redirecionar para a página de rewind
    return redirect('rewind')

def rewind(request):
    # Verificar se o token está na sessão
    token_info = request.session.get('spotify_token')
    if not token_info:
        return redirect('login')
    
    try:
        # Criar cliente Spotify com o token
        sp = spotipy.Spotify(auth=token_info['access_token'])
        
        # Obter as top músicas (últimas 4 semanas)
        top_tracks_short = sp.current_user_top_tracks(limit=10, time_range='short_term')
        
        # Obter informações do usuário
        user_info = sp.current_user()
        
        # Verificar se o token expirou
        if not top_tracks_short['items']:
            # Token pode ter expirado, redirecionar para login
            return redirect('login')
            
        context = {
            'tracks': top_tracks_short['items'],
            'time_range': 'últimas 4 semanas',
            'user': user_info  # Adicionar informações do usuário ao contexto
        }
        
        # Adicionar print para depuração
        print("Renderizando template com contexto:", context.keys())
        
        return render(request, 'Spotify/rewind.html', context)
        
    except Exception as e:
        # Se ocorrer algum erro (como token expirado), redirecionar para login
        import traceback
        print(f"Erro ao acessar Spotify API: {e}")
        print(traceback.format_exc())
        return redirect('login')

def profile(request):
    """
    View para a página de perfil do usuário.
    """
    # Verificar se o token está na sessão (corrigido de token_info para spotify_token)
    token_info = request.session.get('spotify_token')
    if not token_info:
        # Se não houver token, redirecionar para login
        return redirect('login')
    
    try:
        # Criar cliente Spotify com o token
        sp = spotipy.Spotify(auth=token_info['access_token'])
        
        # Obter as top músicas (últimas 4 semanas)
        top_tracks_short = sp.current_user_top_tracks(limit=10, time_range='short_term')
        
        # Obter informações do usuário
        user_info = sp.current_user()
        
        # Verificar se o token expirou
        if not top_tracks_short['items']:
            # Token pode ter expirado, redirecionar para login
            return redirect('login')
            
        context = {
            'tracks': top_tracks_short['items'],
            'user': user_info
        }
        
        return render(request, 'Spotify/profile.html', context)
        
    except Exception as e:
        # Se ocorrer algum erro (como token expirado), redirecionar para login
        import traceback
        print(f"Erro ao acessar Spotify API: {e}")
        print(traceback.format_exc())
        return redirect('login')

def search_track(request):
    """
    View para buscar músicas no Spotify.
    """
    # Verificar se o token está na sessão
    token_info = request.session.get('spotify_token')
    if not token_info:
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    # Obter o termo de busca
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'error': 'Termo de busca não fornecido'}, status=400)
    
    try:
        # Criar cliente Spotify com o token
        sp = spotipy.Spotify(auth=token_info['access_token'])
        
        # Buscar músicas
        results = sp.search(q=query, type='track', limit=8)
        
        # Formatar resultados
        tracks = []
        for item in results['tracks']['items']:
            track = {
                'id': item['id'],
                'name': item['name'],
                'artist': item['artists'][0]['name'],
                'image': item['album']['images'][0]['url'] if item['album']['images'] else '',
                'preview_url': item['preview_url']
            }
            tracks.append(track)
        
        return JsonResponse({'tracks': tracks})
        
    except Exception as e:
        import traceback
        print(f"Erro ao buscar músicas: {e}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)
