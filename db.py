from typing import List, Tuple, Dict, Any
from config import Config
from flask import g
from artist import Artist
import psycopg2

class InvalidArgument(Exception):
    def __init__(self, message: str = ''):
        self.message = message

def get_conn():
    if not hasattr(g, 'db'):
        g.db = psycopg2.connect(
            database = "spotify", 
            user = Config.DB_USER,
            password = Config.DB_PASSWORD, 
            host = Config.DB_HOST, 
            port = Config.DB_PORT
        )
    return g.db 

def create_tables(connection: Any) -> None:
    cursor = connection.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS artists (
            artist_id varchar(42) NOT NULL,
            name varchar(255) NOT NULL,
            PRIMARY KEY (artist_id)
        )'''
    )
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS related_artists (
            artist_id varchar(42) NOT NULL,
            related_id varchar(42) NOT NULL,
            PRIMARY KEY (artist_id, related_id),
            CONSTRAINT artist_id_fk FOREIGN KEY(artist_id) REFERENCES artists(artist_id),
            CONSTRAINT related_id_fk FOREIGN KEY(related_id) REFERENCES artists(artist_id)
        )'''
    )
    cursor.execute('CREATE INDEX ON related_artists (artist_id)')
    cursor.execute('CREATE INDEX ON related_artists (related_id)')
    cursor.execute('CREATE INDEX ON artists (name)')
    cursor.execute('CREATE INDEX full_text ON artists USING GIN (to_tsvector(\'english\', name));')

    
    connection.commit()

def insert_artists(connection: Any, artists: List) -> None:
    if not len(artists):
        return
    cursor = connection.cursor()
    args_list = [
        cursor.mogrify('(%s, %s)', artist).decode('utf-8')
        for artist 
        in artists
    ]
    values = ','.join(args_list)
    cursor.execute(f'INSERT INTO artists VALUES {values} ON CONFLICT (artist_id) DO NOTHING')
    connection.commit()

def insert_related_artists(connection: Any, related_artists: List):
    if not len(related_artists):
        return
    cursor = connection.cursor()
    args_list = [
        cursor.mogrify('(%s, %s)', artist).decode('utf-8')
        for artist 
        in related_artists
    ]
    values = ','.join(args_list)
    cursor.execute(f'INSERT INTO related_artists VALUES {values} ON CONFLICT (artist_id, related_id) DO NOTHING')
    connection.commit()

def get_id(name: str) -> str:
    cursor = get_conn().cursor()
    cursor.execute(
    '''
        SELECT artist_id
        FROM artists
        WHERE to_tsvector(name) @@ to_tsquery('english', %s);
    ''', [f'\'{name}\''])
    res = cursor.fetchall()
    if not len(res):
        raise InvalidArgument(f'No artists match name ${name}')
    return res[0][0]

def get_name(artist_id: str) -> str:
    cursor = get_conn().cursor()
    cursor.execute('SELECT name FROM artists WHERE artist_id = %s', [artist_id])
    res = cursor.fetchone()
    if not res:
        raise InvalidArgument(f'No artists with id {artist_id}')
    return res[0]

def get_related_artists(artist_id: str) -> List[str]:
    cursor = get_conn().cursor()
    cursor.execute(
        '''
        SELECT related_id FROM related_artists WHERE artist_id = %s
        UNION SELECT artist_id FROM related_artists WHERE related_id = %s
        ''',
        [artist_id, artist_id]
    )
    res = cursor.fetchall()
    return [row[0] for row in res]

def query_artist(query: str) -> List[Artist]:
    cursor = get_conn().cursor()
    query = query.replace(' ', ' & ')
    cursor.execute(
    '''
        SELECT *
        FROM artists
        WHERE to_tsvector(name) @@ to_tsquery(%s);
    ''', [f'{query}:*'])
    res = cursor.fetchall()
    return [Artist(row[0], row[1]) for row in res]


def get_all_artists_init(connection: Any) -> List[Artist]:
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM artists')
    res = cursor.fetchall()
    return [Artist(row[0], row[1]) for row in res]
