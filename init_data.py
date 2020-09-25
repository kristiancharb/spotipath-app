from config import Config
from typing import List, Dict
from search import Artist
import requests
import psycopg2
import time
import base64
import db

def get_chartmetric_token() -> str:
    url = 'https://api.chartmetric.com/api/token'
    data = {
        'refreshtoken': Config.CHARTMETRICS_TOKEN
    }
    resp = requests.post(url, data=data)
    return resp.json()['token']

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
    return resp.json()['access_token']

def get_top_artists(token: str) -> List['Artist']:
    url = 'https://api.chartmetric.com/api/charts/airplay/artists?since=2020-09-09&duration=weekly'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    resp = requests.get(url, headers=headers)
    artists = resp.json()['obj']['data']
    return [Artist(artist['spotify_artist_ids'].pop(), artist['name']) for artist in artists]

token = get_chartmetric_token()
top_artists = get_top_artists(token)
token = get_spotify_token()

spotify_headers = {
    'Authorization': f'Bearer {token}'
}

conn = psycopg2.connect(
    database = "spotify", 
    user = Config.DB_USER,
    password = Config.DB_PASSWORD, 
    host = Config.DB_HOST, 
    port = Config.DB_PORT
)

db.create_tables(conn)

db.insert_artists(conn, top_artists)

artists = db.get_all_artists_init(conn)
print(f'Artists fetched from DB: {len(artists)}')
for i, artist in enumerate(artists):
    if i % 20 == 0 and i != 0:
        print(f'Processed {i} artists...')
    url = f'https://api.spotify.com/v1/artists/{artist.artist_id}/related-artists'
    resp = requests.get(url, headers=spotify_headers)

    while resp.status_code == 429:
        print(f'Sleeping: {i}')
        time.sleep(0.3)
        resp = requests.get(url, headers=spotify_headers)

    if resp.status_code != 200:
        print(resp)
        print(resp.json())
        continue
    
    related_artists = [
        Artist(a['id'], a['name'])
        for a in resp.json()['artists']
    ]

    related = [
        (a.artist_id, artist.artist_id)
        for a in related_artists
    ]

    db.insert_artists(conn, related_artists)
    db.insert_related_artists(conn, related)

conn.close()