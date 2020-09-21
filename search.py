import db
import collections
import sys

def trace_path(parents, src, dest):
    path = [dest]
    while path[-1] != src:
        path.append(parents[path[-1]])
    path.reverse()
    return [db.get_name(artist_id) for artist_id in path]

def get_path(src, dest):
    src_id = db.get_id(src)
    dest_id = db.get_id(dest)
    queue = collections.deque([src_id])
    visited = set()
    parents = {}

    while queue:
        curr = queue.pop()
        if curr == dest_id:
            return trace_path(parents, src_id, dest_id)

        for neighbor in db.get_related_artists(curr):
            if neighbor in visited:
                continue
            queue.appendleft(neighbor)
            parents[neighbor] = curr
            visited.add(neighbor)

db.create_tables()
for artist in get_path(sys.argv[1], sys.argv[2]):
    print(artist)