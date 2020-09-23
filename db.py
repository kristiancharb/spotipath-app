from typing import List, Tuple, Dict, Any
from config import Config
from flask import g
import psycopg2

class InvalidArgument(Exception):
    pass

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
    connection.commit()

def insert_artists(connection: Any, artists: Dict) -> None:
    cursor = connection.cursor()
    args_list = [
        cursor.mogrify('(%s, %s)', artist).decode('utf-8')
        for artist 
        in artists.values()
    ]
    cursor.execute('INSERT INTO artists VALUES ' + ','.join(args_list))
    connection.commit()

def insert_related_artists(connection: Any, related_artists: List):
    cursor = connection.cursor()
    args_list = [
        cursor.mogrify('(%s, %s)', artist).decode('utf-8')
        for artist 
        in related_artists
    ]
    cursor.execute('INSERT INTO related_artists VALUES ' + ','.join(args_list))
    connection.commit()

def get_id(name: str) -> str:
    cursor = get_conn().cursor()
    cursor.execute('SELECT artist_id FROM artists WHERE name = %s', [name])
    res = cursor.fetchone()
    if not res:
        raise InvalidArgument()
    return res[0]

def get_name(artist_id: str) -> str:
    cursor = get_conn().cursor()
    cursor.execute('SELECT name FROM artists WHERE artist_id = %s', [artist_id])
    res = cursor.fetchone()
    if not res:
        raise InvalidArgument()
    return res[0]

def get_related_artists(artist_id) -> List[str]:
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

