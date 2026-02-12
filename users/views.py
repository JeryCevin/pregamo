import os
from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests

# --- KONFIGURASI ---
# Menggunakan file 'client_secret.json' yang baru
CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, 'client_secret.json') 

SCOPES = [
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/userinfo.email', 
    'openid'
]
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' 

# --- LOGIN GOOGLE ---
def google_login(request):
    # URL ini mengirim user ke Google
    actual_redirect_uri = request.build_absolute_uri('/users/callback/google/')
    
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=actual_redirect_uri
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    request.session['state'] = state
    return redirect(authorization_url)

# --- CALLBACK (TEMPAT USER PULANG DARI GOOGLE) ---
def google_callback(request):
    state = request.session.get('state')
    if state is None:
        return redirect('/')

    # URL ini harus sama persis dengan yang di google_login
    actual_redirect_uri = request.build_absolute_uri('/users/callback/google/')

    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            state=state,
            redirect_uri=actual_redirect_uri
        )
        
        # Tukar kode izin dengan Token Identitas
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials
        id_token_info = google_id_token.verify_oauth2_token(
            credentials.id_token, requests.Request(), credentials.client_id
        )

        # Ambil data email dan nama dari Google
        email = id_token_info.get('email')
        name = id_token_info.get('name')
        
        # --- (BAGIAN FIREBASE SUDAHDIHAPUS DI SINI) ---

        # --- SIMPAN KE MYSQL (DATABASE LOKAL) ---
        # Cek apakah user sudah ada di database MySQL? Kalau belum, buat baru.
        user, created = User.objects.get_or_create(
            username=email,
            defaults={'email': email, 'first_name': name}
        )
        
        # Login ke Django Session
        login(request, user)
        
        # Berhasil! Masuk ke Dashboard
        return redirect('dashboard') 

    except Exception as e:
        print(f"Error Login: {e}")
        return redirect('/')

# --- LOGOUT ---
def google_logout(request):
    logout(request)
    return redirect('/')