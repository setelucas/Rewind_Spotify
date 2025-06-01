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
from django.urls import path
from django.https import HttpResponse

    def cadastro(request):
        if request.method == 'POST':
            nome = request.POST['nome']
            email = request.POST['email']
            senha = request.POST['senha']
            # Aqui você pode salvar os dados no banco de dados ou fazer qualquer outra ação necessária
            return HttpResponse('Cadastro realizado com sucesso!')
        else:
            return render(request, 'cadastro.html')

    def login(request):
        if request.method == 'POST':
            email = request.POST['email']
            senha = request.POST['senha']
            # Aqui você pode verificar as credenciais do usuário no banco de dados
            # Exemplo de verificação simples (você deve implementar sua própria lógica)
            if email == 'usuario@exemplo.com' and senha == 'senha123':
                return HttpResponse('Login realizado com sucesso!')
            else:
                return HttpResponse('Credenciais inválidas!')
        else:
            return render(request, 'login.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cadastro/', cadastro, name='cadastro'),
    path('login/', login, name='login'),
    path('home/', home, name='home'),
    path('sair/', sair, name='sair'),
]
