import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from config import Config
from typing import List
from search import Artist
import requests
import csv

def get_chartmetric_token() -> str:
    url = 'https://api.chartmetric.com/api/token'
    data = {
        'refreshtoken': Config.CHARTMETRICS_TOKEN
    }
    resp = requests.post(url, data=data)
    return resp.json()['token']

def get_top_artists(token: str) -> List[Artist]:
    url = 'https://api.chartmetric.com/api/charts/airplay/artists?since=2020-09-09&duration=weekly'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    resp = requests.get(url, headers=headers)
    artists = resp.json()['obj']['data']
    return [Artist(artist['spotify_artist_ids'].pop(), artist['name']) for artist in artists]

def write_artists(artists: List[Artist]):
    with open('artists.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        for artist in artists:
            writer.writerow([artist.artist_id, artist.name])

token = get_chartmetric_token()
top_artists = get_top_artists(token)
write_artists(top_artists)