import psycopg2

conn = psycopg2.connect(
    database = "spotify", 
    user = "postgres",
    password = "postgres", 
    host = "localhost", 
    port = "5432")

cursor = conn.cursor()

def create_tables():
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
    conn.commit()

def close():
    conn.close()

def insert_artists(artists):
    args_list = [
        cursor.mogrify('(%s, %s)', artist).decode('utf-8')
        for artist 
        in artists.values()
    ]
    cursor.execute('INSERT INTO artists VALUES ' + ','.join(args_list))
    conn.commit()

def insert_related_artists(related_artists):
    args_list = [
        cursor.mogrify('(%s, %s)', artist).decode('utf-8')
        for artist 
        in related_artists
    ]
    cursor.execute('INSERT INTO related_artists VALUES ' + ','.join(args_list))
    conn.commit()

def get_id(name):
    cursor.execute('SELECT artist_id FROM artists WHERE name = %s', [name])
    res = cursor.fetchone()
    return res[0] if res else None

def get_name(artist_id):
    cursor.execute('SELECT name FROM artists WHERE artist_id = %s', [artist_id])
    res = cursor.fetchone()
    return res[0] if res else None

def get_related_artists(artist_id):
    cursor.execute(
        '''
        SELECT related_id FROM related_artists WHERE artist_id = %s
        UNION SELECT artist_id FROM related_artists WHERE related_id = %s
        ''',
        [artist_id, artist_id]
    )
    res = cursor.fetchall()
    return [row[0] for row in res]

