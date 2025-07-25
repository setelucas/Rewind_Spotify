from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings
import urllib.parse
from .models import SpotifyUser
from django.utils import timezone
import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

def test_view(request):
    """View de teste para verificar se as URLs estão funcionando"""
    return HttpResponse("URLs funcionando! Teste OK.")

def home(request):
    """Página inicial - redireciona para login"""
    return redirect('login')

def spotify_login(request):
    """Página de login - gera URL de autorização do Spotify"""
    # Configurar OAuth do Spotify
    sp_oauth = SpotifyOAuth(
        client_id=settings.SPOTIPY_CLIENT_ID,
        client_secret=settings.SPOTIPY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIPY_REDIRECT_URI,
        scope="user-top-read user-read-private user-read-email"
    )
    
    # Gerar URL de autorização
    auth_url = sp_oauth.get_authorize_url()
    
    # Passar a URL para o template
    return render(request, 'Spotify/login.html', {'auth_url': auth_url})

def callback(request):
    """Callback do Spotify - processa o código de autorização"""
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    if error:
        messages.error(request, f"Erro na autenticação: {error}")
        return redirect('login')
    
    if not code:
        messages.error(request, "Código de autorização não encontrado")
        return redirect('login')
    
    try:
        # Configurar OAuth
        sp_oauth = SpotifyOAuth(
            client_id=settings.SPOTIPY_CLIENT_ID,
            client_secret=settings.SPOTIPY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIPY_REDIRECT_URI,
            scope="user-top-read user-read-private user-read-email"
        )
        
        # Trocar código por token
        token_info = sp_oauth.get_access_token(code)
        
        if token_info:
            # Buscar informações do usuário
            sp = spotipy.Spotify(auth=token_info['access_token'])
            user_info = sp.current_user()
            
            # Salvar ou atualizar usuário no banco
            spotify_user, created = SpotifyUser.objects.update_or_create(
                spotify_id=user_info['id'],
                defaults={
                    'display_name': user_info.get('display_name', ''),
                    'email': user_info.get('email', ''),
                    'profile_image': user_info['images'][0]['url'] if user_info.get('images') else None,
                    'access_token': token_info['access_token'],
                    'refresh_token': token_info.get('refresh_token'),
                    'token_expires_at': timezone.now() + datetime.timedelta(seconds=token_info['expires_in'])
                }
            )
            
            # Salvar ID do usuário na sessão
            request.session['spotify_user_id'] = spotify_user.spotify_id
            
            if created:
                messages.success(request, f"Bem-vindo, {spotify_user.display_name}! Conta criada com sucesso!")
            else:
                messages.success(request, f"Bem-vindo de volta, {spotify_user.display_name}!")
                
            return redirect('profile')
        else:
            messages.error(request, "Erro ao obter token de acesso")
            return redirect('login')
            
    except Exception as e:
        messages.error(request, f"Erro na autenticação: {str(e)}")
        return redirect('login')

def rewind(request):
    """Página de rewind - busca top tracks dos últimos 3 meses"""
    spotify_user_id = request.session.get('spotify_user_id')
    
    if not spotify_user_id:
        messages.error(request, "Você precisa fazer login primeiro")
        return redirect('login')
    
    try:
        # Buscar usuário no banco
        spotify_user = SpotifyUser.objects.get(spotify_id=spotify_user_id)
        
        # Verificar se token expirou
        if spotify_user.is_token_expired():
            messages.error(request, "Sua sessão expirou. Faça login novamente.")
            return redirect('login')
        
        # Criar cliente Spotify
        sp = spotipy.Spotify(auth=spotify_user.access_token)
        
        # Buscar top tracks dos últimos 3 meses (medium_term)
        top_tracks = sp.current_user_top_tracks(
            limit=50,  # Buscar mais músicas
            time_range='medium_term'  # últimos ~6 meses (mais próximo de 3 meses disponível)
        )
        
        # Buscar dados adicionais para cada track
        tracks_data = []
        for track in top_tracks['items']:
            # Buscar informações de áudio da música
            try:
                audio_features = sp.audio_features([track['id']])[0]
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artists': [artist['name'] for artist in track['artists']],
                    'artist_names': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'preview_url': track.get('preview_url'),
                    'external_url': track['external_urls']['spotify'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity'],
                    # Dados de áudio
                    'danceability': audio_features['danceability'] if audio_features else 0,
                    'energy': audio_features['energy'] if audio_features else 0,
                    'valence': audio_features['valence'] if audio_features else 0,
                    'tempo': audio_features['tempo'] if audio_features else 0,
                }
                tracks_data.append(track_info)
            except Exception as e:
                # Se falhar ao buscar audio features, adicionar sem eles
                track_info = {
                    'id': track['id'],
                    'name': track['name'],
                    'artists': [artist['name'] for artist in track['artists']],
                    'artist_names': ', '.join([artist['name'] for artist in track['artists']]),
                    'album': track['album']['name'],
                    'image': track['album']['images'][0]['url'] if track['album']['images'] else None,
                    'preview_url': track.get('preview_url'),
                    'external_url': track['external_urls']['spotify'],
                    'duration_ms': track['duration_ms'],
                    'popularity': track['popularity'],
                    'danceability': 0,
                    'energy': 0,
                    'valence': 0,
                    'tempo': 0,
                }
                tracks_data.append(track_info)
        
        context = {
            'top_tracks': tracks_data,
            'total_tracks': len(tracks_data),
            'spotify_user': spotify_user,
            'time_period': 'últimos 6 meses'  # Spotify não tem exatamente 3 meses
        }
        
        return render(request, 'Spotify/rewind.html', context)
        
    except SpotifyUser.DoesNotExist:
        messages.error(request, "Usuário não encontrado. Faça login novamente.")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"Erro ao buscar dados do Spotify: {str(e)}")
        return redirect('login')

def profile(request):
    """Página de perfil - busca dados do usuário logado"""
    spotify_user_id = request.session.get('spotify_user_id')
    
    if not spotify_user_id:
        messages.error(request, "Você precisa fazer login primeiro")
        return redirect('login')
    
    try:
        # Buscar usuário no banco
        spotify_user = SpotifyUser.objects.get(spotify_id=spotify_user_id)
        
        # Verificar se token expirou
        if spotify_user.is_token_expired():
            messages.error(request, "Sua sessão expirou. Faça login novamente.")
            return redirect('login')
        
        # Criar cliente Spotify
        sp = spotipy.Spotify(auth=spotify_user.access_token)
        
        # Buscar informações atualizadas
        user_info = sp.current_user()
        top_tracks = sp.current_user_top_tracks(limit=5, time_range='medium_term')
        
        context = {
            'user_info': user_info,
            'top_tracks': top_tracks['items'],
            'spotify_user': spotify_user,
            'message': f'Bem-vindo, {user_info.get("display_name", "Usuário")}!'
        }
        
        return render(request, 'Spotify/profile.html', context)
        
    except SpotifyUser.DoesNotExist:
        messages.error(request, "Usuário não encontrado. Faça login novamente.")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"Erro ao buscar dados do Spotify: {str(e)}")
        return redirect('login')

def logout(request):
    """Logout - limpa sessão"""
    if 'spotify_user_id' in request.session:
        del request.session['spotify_user_id']
    messages.success(request, "Logout realizado com sucesso!")
    return redirect('login')

def login_alt(request):
    """Página de login alternativa"""
    return render(request, 'Spotify/auth/login_alt.html')

def register_user(request):
    """Página de registro de usuário"""
    if request.method == 'POST':
        # Pegar dados do formulário
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        terms = request.POST.get('terms')
        newsletter = request.POST.get('newsletter')
        
        # Validações
        if not all([first_name, last_name, username, email, password1, password2]):
            messages.error(request, "Todos os campos obrigatórios devem ser preenchidos")
            return render(request, 'Spotify/auth/register.html')
        
        if password1 != password2:
            messages.error(request, "As senhas não coincidem")
            return render(request, 'Spotify/auth/register.html')
        
        if len(password1) < 6:
            messages.error(request, "A senha deve ter pelo menos 6 caracteres")
            return render(request, 'Spotify/auth/register.html')
        
        if not terms:
            messages.error(request, "Você deve aceitar os termos de uso")
            return render(request, 'Spotify/auth/register.html')
        
        # Verificar se usuário já existe
        if User.objects.filter(username=username).exists():
            messages.error(request, "Nome de usuário já existe")
            return render(request, 'Spotify/auth/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email já cadastrado")
            return render(request, 'Spotify/auth/register.html')
        
        try:
            # Criar usuário
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            # Fazer login automático
            user = authenticate(username=username, password=password1)
            if user:
                login(request, user)
                messages.success(request, f"Conta criada com sucesso! Bem-vindo, {first_name}!")
                return redirect('dashboard')
            else:
                messages.success(request, "Conta criada com sucesso! Faça login para continuar.")
                return redirect('login_alt')
                
        except Exception as e:
            messages.error(request, f"Erro ao criar conta: {str(e)}")
            return render(request, 'Spotify/auth/register.html')
    
    return render(request, 'Spotify/auth/register.html')

def dashboard(request):
    """Dashboard do usuário"""
    spotify_user_id = request.session.get('spotify_user_id')
    
    if not spotify_user_id:
        messages.error(request, "Você precisa fazer login primeiro")
        return redirect('login')
    
    try:
        spotify_user = SpotifyUser.objects.get(spotify_id=spotify_user_id)
        context = {
            'spotify_user': spotify_user,
        }
        return render(request, 'Spotify/user/dashboard.html', context)
    except SpotifyUser.DoesNotExist:
        messages.error(request, "Usuário não encontrado")
        return redirect('login')

def user_settings(request):
    """Configurações do usuário"""
    spotify_user_id = request.session.get('spotify_user_id')
    
    if not spotify_user_id:
        messages.error(request, "Você precisa fazer login primeiro")
        return redirect('login')
    
    try:
        spotify_user = SpotifyUser.objects.get(spotify_id=spotify_user_id)
        context = {
            'spotify_user': spotify_user,
        }
        return render(request, 'Spotify/user/settings.html', context)
    except SpotifyUser.DoesNotExist:
        messages.error(request, "Usuário não encontrado")
        return redirect('login')
