import requests
import collections
import db
import time

url = 'https://accounts.spotify.com/api/token'
headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Authorization': 'Basic ZWI3ZTJmZTE0MDkxNDcyZTgzMGY2M2QzNWJiOTg4MTk6YzU3YjBmOTQxYzNiNDFiMWE5YmQ1NjhkNTBhYjIzMTg=' 
}
data = {
    'grant_type': 'client_credentials' 
}
resp = requests.post(url, data=data, headers=headers)
token = resp.json()['access_token']

db.create_tables()

visited_artists = {}
related_artists = []

headers = {
    'Authorization': f'Bearer {token}'
}

queue = collections.deque([('5K4W6rqBFWDnAN6FQUkS6x', 'Kanye West')])

for i in range(1000):
    artist_id, artist_name = queue.pop()
    url = f'https://api.spotify.com/v1/artists/{artist_id}/related-artists'
    resp = requests.get(url, headers=headers)

    if resp.status_code == 429:
        queue.append((artist_id, artist_name))
        print(f'Sleeping: {i}')
        time.sleep(0.1)
        continue

    if resp.status_code != 200:
        print(resp)
        print(resp.json())
        continue
    artists = resp.json()['artists']

    for artist in artists:
        curr_id, curr_name = artist['id'], artist['name']

        if curr_id not in visited_artists:
            queue.appendleft((curr_id, curr_name))
            visited_artists[curr_id] = (curr_id, curr_name)
            related_artists.append((artist_id, curr_id))

    if i % 50 == 0:
        print(f'Processed {i} artists')

db.insert_artists(visited_artists)
db.insert_related_artists(related_artists)
db.close()