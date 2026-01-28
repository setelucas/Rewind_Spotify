 Visão Geral do Projeto

O Rewind Spotify é um projeto de estudo desenvolvido com o objetivo de explorar, na prática, a integração entre uma aplicação web em **Django (Python)** e a **API oficial do Spotify**. A ideia central do projeto é permitir que um usuário se autentique com sua conta do Spotify e visualize um resumo personalizado do seu consumo musical — inspirado no conceito do *Spotify Wrapped*.

Mais do que um produto final, este projeto foi pensado como um **laboratório de aprendizado**, servindo para consolidar conceitos importantes de backend, autenticação e consumo de APIs externas.

---

 Objetivo do Projeto

O principal objetivo do Rewind Spotify é:

* Entender como funciona o *fluxo de autenticação OAuth 2.0* utilizando um provedor real (Spotify)
* Consumir dados reais de usuários a partir de uma *API REST*
* Estruturar uma aplicação web utilizando o *framework Django*
* Trabalhar com rotas, views, templates e controle de sessão

O projeto não se encontra finalizado, mas cumpre seu papel como base técnica e conceitual para aplicações mais complexas.

---

 Como o Projeto Funciona

De forma resumida, o funcionamento do projeto segue o fluxo abaixo:

1. O usuário acessa a aplicação web
2. A aplicação solicita autenticação via Spotify
3. O usuário é redirecionado para a página oficial de login do Spotify
4. Após a autorização, o Spotify retorna um *access token*
5. A aplicação utiliza esse token para consumir dados do usuário (como artistas e músicas mais ouvidas)
6. Esses dados são processados e exibidos em páginas HTML

Esse fluxo simula o comportamento de aplicações reais que dependem de serviços externos para funcionar.

---

 Estrutura Geral do Código

O projeto segue a estrutura padrão de um projeto Django:

* *Projeto Django principal*: responsável pelas configurações globais (settings, urls, wsgi/asgi)
* *App principal (`spotify_app`)*: concentra a lógica relacionada à autenticação com o Spotify e à exibição dos dados
* *Views*: controlam o fluxo da aplicação, como login, callback do Spotify e páginas de visualização
* *Templates*: responsáveis pela camada visual da aplicação

Essa separação ajuda a manter o código organizado e facilita futuras manutenções ou expansões.

---

 Integração com a API do Spotify

A comunicação com o Spotify é feita através da *Spotify Web API*, utilizando o fluxo de autenticação OAuth 2.0.

Principais pontos dessa integração:

* Uso de **Client ID** e *Client Secret* (fornecidos pelo Spotify Developer Dashboard)
* Redirecionamento do usuário para autorização
* Recebimento e armazenamento temporário do *access token*
* Requisições autenticadas para buscar dados do usuário

Essa etapa foi fundamental para compreender como funcionam permissões, escopos e tokens de acesso em APIs modernas.

---

 Estado Atual do Projeto

O Rewind Spotify é um projeto *incompleto e em pausa*, mas totalmente funcional como base de estudo.

Ele representa um momento importante de aprendizado e permanece como:

* Registro de evolução técnica
* Referência para projetos futuros
* Base para possíveis melhorias e novas funcionalidades

---

 Próximos Passos (Ideias Futuras)

Algumas evoluções possíveis para o projeto:

* Melhorar a interface visual
* Criar gráficos e estatísticas musicais
* Gerar relatórios de retrospectiva
* Criar playlists automaticamente
* Preparar a aplicação para deploy em produção

---

 Como Rodar o Projeto Localmente

Abaixo estão os passos básicos para executar o projeto em ambiente local. O processo segue o padrão de aplicações Django.

 1. Pré-requisitos

Antes de começar, certifique-se de ter instalado:

* Python 3.10 ou superior
* Git
* Conta no Spotify Developer Dashboard

---

 2. Clonar o Repositório

```bash
git clone https://github.com/setelucas/Rewind_Spotify.git
cd Rewind_Spotify
```

---

3. Criar e Ativar um Ambiente Virtual (venv)

```bash
python -m venv venv
```

Ativando o ambiente virtual:

* *Windows*

```bash
venv\Scripts\activate
```

* *Linux / macOS*

```bash
source venv/bin/activate
```

---

 4. Instalar as Dependências

```bash
pip install -r requirements.txt
```

---

 5. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto e adicione suas credenciais do Spotify:

```env
SPOTIFY_CLIENT_ID=seu_client_id
SPOTIFY_CLIENT_SECRET=seu_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8000/callback/
```

Essas credenciais podem ser obtidas no *Spotify Developer Dashboard* ao criar uma aplicação.

---

 6. Aplicar as Migrações do Banco de Dados

```bash
python manage.py migrate
```

---

 7. Rodar o Servidor de Desenvolvimento

```bash
python manage.py runserver
```

Após isso, a aplicação estará disponível em:

```
http://localhost:8000/
```

---

 8. Fluxo de Uso

1. Acesse a aplicação no navegador
2. Clique para autenticar com o Spotify
3. Autorize o acesso
4. Visualize os dados retornados pela API

---

Este projeto reforça a ideia de que aprender desenvolvimento é um processo contínuo — e cada projeto, completo ou não, contribui para essa jornada 🚀

