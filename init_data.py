from config import Config
from typing import List, Dict
import requests
import psycopg2
import collections
import time
import base64
import db

Artist = collections.namedtuple('Artist', ('artist_id', 'name'))

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

for j, a in enumerate(top_artists):
    queue = collections.deque([a])
    visited = set([a.artist_id])
    artists = {a.artist_id: a}
    related = []
    for i in range(100):
        if i % 20 == 0 and i != 0:
            print(f'Processed {i} artists')

        if not queue:
            break
        artist = queue.pop()
        url = f'https://api.spotify.com/v1/artists/{artist.artist_id}/related-artists'
        resp = requests.get(url, headers=spotify_headers)

        if resp.status_code == 429:
            queue.append(artist)
            print(f'Sleeping: {i}')
            time.sleep(0.2)
            continue
        elif resp.status_code != 200 or 'artists' not in resp.json():
            print(resp.json())
            continue
        
        related_artists = [
            Artist(a['id'], a['name']) 
            for a in resp.json()['artists']
        ]

        for related_artist in related_artists:
            if related_artist.artist_id not in visited:
                queue.appendleft(related_artist)
                related.append((artist.artist_id, related_artist.artist_id))
                artists[related_artist.artist_id] = related_artist

        visited.add(artist.artist_id)

    db.insert_artists(conn, list(artists.values()))
    db.insert_related_artists(conn, related)
    print(f'Inserted rows ({j}')

conn.close()
# conn = psycopg2.connect(
#             database = "spotify", 
#             user = Config.DB_USER,
#             password = Config.DB_PASSWORD, 
#             host = Config.DB_HOST, 
#             port = Config.DB_PORT
# )

# visited_artists = {}
# related_artists = []

# headers = {
#     'Authorization': f'Bearer {token}'
# }

# queue = collections.deque([('5K4W6rqBFWDnAN6FQUkS6x', 'Kanye West')])

# for i in range(100000):
#     artist_id, artist_name = queue.pop()
#     url = f'https://api.spotify.com/v1/artists/{artist_id}/related-artists'
#     resp = requests.get(url, headers=headers)

#     if resp.status_code == 429:
#         queue.append((artist_id, artist_name))
#         print(f'Sleeping: {i}')
#         time.sleep(0.1)
#         continue

#     if resp.status_code != 200:
#         print(resp)
#         print(resp.json())
#         continue
#     artists = resp.json()['artists']

#     for artist in artists:
#         curr_id, curr_name = artist['id'], artist['name']

#         if curr_id not in visited_artists:
#             queue.appendleft((curr_id, curr_name))
#             visited_artists[curr_id] = (curr_id, curr_name)
#             related_artists.append((artist_id, curr_id))

#     if i % 50 == 0:
#         print(f'Processed {i} artists')

# db.insert_artists(conn, visited_artists)
# db.insert_related_artists(conn, related_artists)
# conn.close()