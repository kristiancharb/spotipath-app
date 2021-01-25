# Spotipath API

### Inspiration
Spotipath was inspired by [Boil the Frog](http://boilthefrog.playlistmachinery.com/).
I thought it was a really cool way of using the Spotify API and decided I wanted to try my hand
at recreating it and maybe figuring out a way to put my own spin on it. 

### How it works
I pre-fetched artist data for roughly 16,000 artists (this includes their related artists) and stored 
it in a database. The path finding algorithm uses bidirectional BFS. 

When a request is made for a path 
between two artists, the algorithm visits those artists' related artists, and their related artists' 
related artists, and so on. When an artist is encountered that was already encountered by the scan starting
at the other artist, the algorithm terminates. The algorithm backtracks down the visited path back 
to each of the starting artists and returns that path.

### API

| Method 	| Path          	| Params                                                   	| Response                                                                                                                                	|
|--------	|---------------	|----------------------------------------------------------	|-----------------------------------------------------------------------------------------------------------------------------------------	|
| GET    	| /path         	| - `src` (required, string)<br>- `dest` (required, string 	| Fetches path `src` and `dest` artist through related artists.<br>Returns array of artists: <br>`[{id: '123', name: 'Kanye West'}, ...]` 	|
| GET    	| /artists      	| - `q` (required, string)                                 	| Performs a full text search using `q` as the query string and returns array of artists: <br>`[{id: '123', name: 'Kanye West'}, ...      	|
| GET    	| /access-token 	|                                                          	| Returns a Spotify access token that is valid for<br>1 hour:<br> `{token: '12345'}`                                                      	|

### How to Run
```
$ pip install flask flask_cors psycopg2 requests
$ cd data
$ python3 init_data.py
$ cd ..
$ export FLASK_APP=server.py
$ flask run
```


