import requests
import base64
from config import Config

def get_spotify_token() -> str:
    url = 'https://accounts.spotify.com/api/token'
    spotify_auth = f'{Config.SPOTIFY_CLIENT_ID}:{Config.SPOTIFY_CLIENT_SECRET}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {base64.b64encode(spotify_auth.encode()).decode()}'
    }
    data = {
        'grant_type': 'client_credentials' 
    }
    resp = requests.post(url, data=data, headers=headers)
    token = resp.json().get('access_token');
    if resp.ok and token:
        return token
    else: 
        raise Exception()