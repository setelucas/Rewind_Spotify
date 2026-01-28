 Project Overview

*Rewind Spotify* is a study project developed with the goal of exploring, in practice, the integration between a web application built with *Django (Python)* and the **official Spotify API**.

The core idea of the project is to allow users to authenticate with their Spotify account and view a personalized summary of their music listening habits — inspired by the *Spotify Wrapped* concept.

More than a finished product, this project was designed as a **learning laboratory**, aimed at consolidating important concepts related to backend development, authentication, and external API consumption.

---

 Project Goals

The main goals of Rewind Spotify are:

* To understand how the **OAuth 2.0 authentication flow** works using a real provider (Spotify)
* To consume real user data from a *REST API*
* To structure a web application using the **Django framework**
* To work with routes, views, templates, and session management

Although the project is not finished, it fulfills its role as a technical and conceptual foundation for more complex applications.

---

 How the Project Works

At a high level, the project follows the flow below:

1. The user accesses the web application
2. The application requests authentication via Spotify
3. The user is redirected to Spotify’s official login page
4. After authorization, Spotify returns an *access token*
5. The application uses this token to consume user data (such as top artists and tracks)
6. The data is processed and displayed on HTML pages

This flow simulates the behavior of real-world applications that depend on external services.

---

 General Code Structure

The project follows the standard Django project structure:

* *Main Django project*: responsible for global configurations (settings, urls, wsgi/asgi)
* *Main app (`spotify_app`)*: contains the logic related to Spotify authentication and data display
* *Views*: control the application flow, such as login, Spotify callback, and data visualization pages
* *Templates*: responsible for the visual layer of the application

This separation helps keep the code organized and makes future maintenance or expansion easier.

---

 Spotify API Integration

Communication with Spotify is handled through the **Spotify Web API**, using the OAuth 2.0 authentication flow.

Key points of this integration include:

* Use of *Client ID* and *Client Secret* (provided by the Spotify Developer Dashboard)
* Redirecting the user for authorization
* Receiving and temporarily storing the *access token*
* Making authenticated requests to fetch user data

This step was essential to understanding how permissions, scopes, and access tokens work in modern APIs.

---

 Current Project Status

Rewind Spotify is an *incomplete and paused project*, but fully functional as a learning base.

It represents an important stage of technical growth and remains as:

* A record of technical evolution
* A reference for future projects
* A foundation for possible improvements and new features

---

 Next Steps (Future Ideas)

Some possible future improvements include:

* Enhancing the user interface
* Creating charts and music statistics
* Generating retrospective reports
* Automatically creating playlists
* Preparing the application for production deployment

---

 How to Run the Project Locally

Below are the basic steps to run the project in a local development environment. The process follows the standard Django workflow.

 1. Prerequisites

Before starting, make sure you have the following installed:

* Python 3.10 or higher
* Git
* A Spotify Developer Dashboard account

---

 2. Clone the Repository

```bash
git clone https://github.com/setelucas/Rewind_Spotify.git
cd Rewind_Spotify
```

---

 3. Create and Activate a Virtual Environment (venv)

```bash
python -m venv venv
```

Activate the virtual environment:

* *Windows*

```bash
venv\Scripts\activate
```

* *Linux / macOS*

```bash
source venv/bin/activate
```

---

 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

 5. Configure Environment Variables

Create a `.env` file in the root directory and add your Spotify credentials:

```env
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8000/callback/
```

These credentials can be obtained from the *Spotify Developer Dashboard* after creating an application.

---

 6. Apply Database Migrations

```bash
python manage.py migrate
```

---

 7. Run the Development Server

```bash
python manage.py runserver
```

The application will be available at:

```
http://localhost:8000/
```

---

 8. Usage Flow

1. Access the application in your browser
2. Click to authenticate with Spotify
3. Grant the requested permissions
4. View the data returned by the Spotify API

---

If you want, next I can:

* Help you *merge PT-BR + EN in one README*
* Polish the English to sound even more **open-source / international**
* Add a *“Technical Decisions”* or *“Architecture Overview”* section
