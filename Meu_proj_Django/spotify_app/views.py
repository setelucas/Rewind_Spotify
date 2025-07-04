import time
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.conf import settings
from django.utils import timezone
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.core.cache import cache
from .models import SpotifyUser
from django.contrib import messages

def get_spotify_client(request):
    """
    Função auxiliar para obter um cliente Spotify com token válido.
    Verifica se o token está expirado e o renova automaticamente se necessário.
    """
    # Obter o ID do usuário Spotify da sessão
    spotify_user_id = request.session.get('spotify_user_id')
    
    # Se não há ID do usuário na sessão, retornar None
    if not spotify_user_id:
        return None
    
    try:
        # Obter o usuário do banco de dados
        spotify_user = SpotifyUser.objects.get(spotify_id=spotify_user_id)
        
        # Verificar se o token está expirado
        if spotify_user.is_token_expired():
            # Tentar renovar o token
            sp_oauth = SpotifyOAuth(
                client_id=settings.SPOTIPY_CLIENT_ID,
                client_secret=settings.SPOTIPY_CLIENT_SECRET,
                redirect_uri=settings.SPOTIPY_REDIRECT_URI,
                scope="user-top-read user-read-email user-read-private"
            )
            
            if spotify_user.refresh_token:
                try:
                    # Renovar o token usando o refresh_token
                    new_token = sp_oauth.refresh_access_token(spotify_user.refresh_token)
                    
                    # Atualizar o token no banco de dados
                    spotify_user.access_token = new_token['access_token']
                    if 'refresh_token' in new_token:
                        spotify_user.refresh_token = new_token['refresh_token']
                    
                    # Calcular nova data de expiração
                    spotify_user.token_expires_at = timezone.now() + timezone.timedelta(seconds=new_token['expires_in'])
                    spotify_user.save()
                except Exception as e:
                    print(f"Erro ao renovar token: {e}")
                    return None
            else:
                # Se não há refresh_token, retornar None para forçar novo login
                return None
        
        # Criar e retornar o cliente Spotify
        return spotipy.Spotify(auth=spotify_user.access_token)
        
    except SpotifyUser.DoesNotExist:
        # Se o usuário não existe no banco de dados, retornar None
        return None
    except Exception as e:
        # Se ocorrer erro na renovação, retornar None
        print(f"Erro ao obter cliente Spotify: {e}")
        return None

def spotify_login(request):
    # Limpar qualquer sessão existente para evitar conflitos
    if 'spotify_user_id' in request.session:
        del request.session['spotify_user_id']
    
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-top-read user-read-email user-read-private"
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

def callback(request):
    try:
        # Verificar se há um erro no callback do Spotify
        error = request.GET.get('error')
        if error:
            print(f"Erro retornado pelo Spotify: {error}")
            messages.error(request, f"Erro de autenticação: {error}")
            return render(request, 'Spotify/login.html', {'error': error})
        
        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIPY_CLIENT_ID,
            client_secret=settings.SPOTIPY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIPY_REDIRECT_URI,
            scope="user-top-read user-read-email user-read-private"
        )
        
        code = request.GET.get('code')
        if not code:
            messages.error(request, "Código de autorização não fornecido")
            return render(request, 'Spotify/login.html')
            
        token_info = sp_oauth.get_access_token(code)
        
        # Criar cliente Spotify com o token
        sp = spotipy.Spotify(auth=token_info['access_token'])
        
        # Obter informações do usuário
        user_info = sp.current_user()
        
        # Calcular quando o token expira
        expires_at = timezone.now() + timezone.timedelta(seconds=token_info['expires_in'])
        
        # Verificar se já existe um usuário com este ID na sessão
        old_user_id = request.session.get('spotify_user_id')
        if old_user_id and old_user_id != user_info['id']:
            # Se estamos trocando de usuário, limpar o cache do usuário anterior
            cache.delete(f'top_tracks_short_{old_user_id}')
            cache.delete(f'user_info_{old_user_id}')
        
        # Salvar ou atualizar o usuário no banco de dados
        spotify_user, created = SpotifyUser.objects.update_or_create(
            spotify_id=user_info['id'],
            defaults={
                'display_name': user_info.get('display_name'),
                'email': user_info.get('email'),
                'profile_image': user_info.get('images')[0]['url'] if user_info.get('images') else None,
                'access_token': token_info['access_token'],
                'refresh_token': token_info.get('refresh_token', ''),
                'token_expires_at': expires_at,
            }
        )
        
        # Salvar o ID do usuário Spotify na sessão
        request.session['spotify_user_id'] = spotify_user.spotify_id
        
        # Redirecionar para a página de rewind
        return redirect('rewind')
        
    except Exception as e:
        import traceback
        print(f"Erro no callback do Spotify: {e}")
        print(traceback.format_exc())
        # Em vez de redirecionar, renderizar uma página de erro
        messages.error(request, f"Erro ao processar autenticação: {str(e)}")
        return render(request, 'Spotify/error.html', {'error': str(e)})

def rewind(request):
    # Obter cliente Spotify com token válido
    sp = get_spotify_client(request)
    if not sp:
        messages.warning(request, "Sessão expirada. Por favor, faça login novamente.")
        return redirect('login')
    
    try:
        # Obter o ID do usuário Spotify da sessão
        spotify_user_id = request.session.get('spotify_user_id')
        
        # Tentar obter dados do cache
        cache_key_tracks = f'top_tracks_short_{spotify_user_id}'
        cache_key_user = f'user_info_{spotify_user_id}'
        
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
            messages.info(request, "Não encontramos dados recentes. Tente novamente.")
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
        messages.error(request, "Ocorreu um erro ao acessar seus dados do Spotify.")
        return render(request, 'Spotify/error.html', {'error': str(e)})

def profile(request):
    """
    View para a página de perfil do usuário.
    """
    # Obter cliente Spotify com token válido
    sp = get_spotify_client(request)
    if not sp:
        return redirect('login')
    
    try:
        # Obter o ID do usuário Spotify da sessão
        spotify_user_id = request.session.get('spotify_user_id')
        
        # Tentar obter dados do cache
        cache_key_tracks = f'top_tracks_short_{spotify_user_id}'
        cache_key_user = f'user_info_{spotify_user_id}'
        
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
    # Obter o ID do usuário Spotify da sessão
    spotify_user_id = request.session.get('spotify_user_id')
    
    if not spotify_user_id:
        return redirect('login')
    
    try:
        # Limpar cache do usuário
        cache.delete(f'top_tracks_short_{spotify_user_id}')
        cache.delete(f'user_info_{spotify_user_id}')
        
        # Redirecionar para a página anterior ou para rewind
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('rewind')
    except Exception as e:
        print(f"Erro ao limpar cache: {e}")
        return redirect('login')

def logout(request):
    """
    View para fazer logout do usuário e permitir login com outra conta.
    Limpa a sessão, cache e redireciona para a página de login.
    """
    # Obter o ID do usuário Spotify da sessão
    spotify_user_id = request.session.get('spotify_user_id')
    
    # Limpar cache específico do usuário
    if spotify_user_id:
        cache.delete(f'top_tracks_short_{spotify_user_id}')
        cache.delete(f'user_info_{spotify_user_id}')
    
    # Limpar a sessão
    request.session.flush()
    
    # Limpar o cache do spotipy (.cache)
    import os
    cache_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.cache')
    if os.path.exists(cache_path):
        try:
            os.remove(cache_path)
        except Exception as e:
            print(f"Erro ao remover arquivo de cache: {e}")
    
    # Redirecionar para a página de login com parâmetro para forçar nova autenticação
    return redirect('login_new_account')

def login_new_account(request):
    """
    View para forçar login com uma nova conta Spotify.
    Adiciona parâmetros para evitar o uso de tokens em cache.
    """
    # Limpar a sessão atual
    request.session.flush()
    
    # Adicionar mensagem
    messages.info(request, "Por favor, faça login com sua conta Spotify. Se já estiver logado no Spotify, você pode clicar em 'Usar outra conta'.")
    
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-top-read user-read-email user-read-private"
    )
    
    # Adicionar parâmetro show_dialog=true para forçar a tela de login do Spotify
    auth_url = sp_oauth.get_authorize_url(show_dialog=True)
    return redirect(auth_url)
