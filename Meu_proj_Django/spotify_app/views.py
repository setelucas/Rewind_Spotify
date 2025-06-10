import time
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.conf import settings
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.core.cache import cache

def get_spotify_client(request):
    """
    Função auxiliar para obter um cliente Spotify com token válido.
    Verifica se o token está expirado e o renova automaticamente se necessário.
    """
    token_info = request.session.get('spotify_token')
    
    # Se não há token, retornar None
    if not token_info:
        return None
    
    # Verificar se o token está expirado
    now = int(time.time())
    is_expired = token_info.get('expires_at', 0) - now < 60
    
    # Se o token está expirado, tentar renová-lo
    if is_expired:
        try:
            sp_oauth = SpotifyOAuth(
                client_id=settings.SPOTIPY_CLIENT_ID,
                client_secret=settings.SPOTIPY_CLIENT_SECRET,
                redirect_uri=settings.SPOTIPY_REDIRECT_URI,
                scope="user-top-read"
            )
            
            if 'refresh_token' in token_info:
                # Renovar o token usando o refresh_token
                new_token = sp_oauth.refresh_access_token(token_info['refresh_token'])
                # Atualizar o timestamp
                new_token['timestamp'] = int(time.time())
                # Atualizar a sessão
                request.session['spotify_token'] = new_token
                token_info = new_token
            else:
                # Se não há refresh_token, retornar None para forçar novo login
                return None
        except Exception as e:
            # Se ocorrer erro na renovação, retornar None
            print(f"Erro ao renovar token: {e}")
            return None
    
    # Criar e retornar o cliente Spotify
    return spotipy.Spotify(auth=token_info['access_token'])

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
    
    # Adicionar timestamp atual para controle de expiração
    token_info['timestamp'] = int(time.time())
    
    # Salvar o token na sessão
    request.session['spotify_token'] = token_info
    
    # Redirecionar para a página de rewind
    return redirect('rewind')

def rewind(request):
    # Obter cliente Spotify com token válido
    sp = get_spotify_client(request)
    if not sp:
        return redirect('login')
    
    try:
        # Tentar obter dados do cache
        user_id = sp.current_user()['id']
        cache_key_tracks = f'top_tracks_short_{user_id}'
        cache_key_user = f'user_info_{user_id}'
        
        top_tracks_short = cache.get(cache_key_tracks)
        user_info = cache.get(cache_key_user)
        
        # Se não estiver no cache, buscar da API
        if not top_tracks_short:
            top_tracks_short = sp.current_user_top_tracks(limit=10, time_range='short_term')
            # Armazenar no cache por 5 minutos
            cache.set(cache_key_tracks, top_tracks_short, 300)
        
        if not user_info:
            user_info = sp.current_user()
            # Armazenar no cache por 30 minutos (informações do usuário mudam menos)
            cache.set(cache_key_user, user_info, 1800)
        
        # Verificar se a resposta está vazia
        if not top_tracks_short['items']:
            # Limpar cache e redirecionar para login
            cache.delete(cache_key_tracks)
            return redirect('login')
            
        context = {
            'tracks': top_tracks_short['items'],
            'time_range': 'últimas 4 semanas',
            'user': user_info
        }
        
        return render(request, 'Spotify/rewind.html', context)
        
    except Exception as e:
        # Se ocorrer algum erro, redirecionar para login
        import traceback
        print(f"Erro ao acessar Spotify API: {e}")
        print(traceback.format_exc())
        return redirect('login')

def profile(request):
    """
    View para a página de perfil do usuário.
    """
    # Obter cliente Spotify com token válido
    sp = get_spotify_client(request)
    if not sp:
        return redirect('login')
    
    try:
        # Tentar obter dados do cache
        user_id = sp.current_user()['id']
        cache_key_tracks = f'top_tracks_short_{user_id}'
        cache_key_user = f'user_info_{user_id}'
        
        top_tracks_short = cache.get(cache_key_tracks)
        user_info = cache.get(cache_key_user)
        
        # Se não estiver no cache, buscar da API
        if not top_tracks_short:
            top_tracks_short = sp.current_user_top_tracks(limit=10, time_range='short_term')
            # Armazenar no cache por 5 minutos
            cache.set(cache_key_tracks, top_tracks_short, 300)
        
        if not user_info:
            user_info = sp.current_user()
            # Armazenar no cache por 30 minutos
            cache.set(cache_key_user, user_info, 1800)
        
        # Verificar se a resposta está vazia
        if not top_tracks_short['items']:
            # Limpar cache e redirecionar para login
            cache.delete(cache_key_tracks)
            return redirect('login')
            
        context = {
            'tracks': top_tracks_short['items'],
            'user': user_info
        }
        
        return render(request, 'Spotify/profile.html', context)
        
    except Exception as e:
        import traceback
        print(f"Erro ao acessar Spotify API: {e}")
        print(traceback.format_exc())
        return redirect('login')

def search_track(request):
    """
    View para buscar músicas no Spotify.
    """
    # Obter cliente Spotify com token válido
    sp = get_spotify_client(request)
    if not sp:
        return JsonResponse({'error': 'Não autenticado'}, status=401)
    
    # Obter o termo de busca
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'error': 'Termo de busca não fornecido'}, status=400)
    
    try:
        # Tentar obter resultados do cache
        cache_key = f'search_results_{query}'
        cached_results = cache.get(cache_key)
        
        if cached_results:
            return JsonResponse({'tracks': cached_results})
        
        # Se não estiver no cache, buscar da API
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
        
        # Armazenar no cache por 1 hora (resultados de busca mudam menos)
        cache.set(cache_key, tracks, 3600)
        
        return JsonResponse({'tracks': tracks})
        
    except Exception as e:
        import traceback
        print(f"Erro ao buscar músicas: {e}")
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)}, status=500)

def clear_user_cache(request):
    """
    View para limpar o cache do usuário.
    Útil quando o usuário quer forçar uma atualização dos dados.
    """
    if not request.session.get('spotify_token'):
        return redirect('login')
    
    try:
        # Obter ID do usuário
        sp = get_spotify_client(request)
        if sp:
            user_id = sp.current_user()['id']
            
            # Limpar cache do usuário
            cache.delete(f'top_tracks_short_{user_id}')
            cache.delete(f'user_info_{user_id}')
            
            # Redirecionar para a página anterior ou para rewind
            referer = request.META.get('HTTP_REFERER')
            if referer:
                return redirect(referer)
            return redirect('rewind')
        
        return redirect('login')
    except Exception as e:
        print(f"Erro ao limpar cache: {e}")
        return redirect('login')
