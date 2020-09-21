from typing import List, Dict, Set
import db
import collections
import sys

class BFS:
    def __init__(self, node_id: str):
        self.id = node_id
        self.queue = collections.deque([node_id])
        self.curr: str = None
        self.parents: Dict[str, str] = {}
        self.visited: Set[str] = set()

    def visit_neighbors(self) -> None:
        for neighbor in db.get_related_artists(self.curr):
            if neighbor in self.visited:
                continue
            self.queue.appendleft(neighbor)
            self.parents[neighbor] = self.curr
            self.visited.add(neighbor)

def trace_path(parents: List[str], src: str, dest: str) -> List[str]:
    path = [dest]
    while path[-1] != src:
        path.append(parents[path[-1]])
    return [db.get_name(artist_id) for artist_id in path]

def get_path(src: str, dest: str) -> List[str]:
    src_id = db.get_id(src)
    dest_id = db.get_id(dest)
    src_queue = collections.deque([src_id])
    dest_queue = collections.deque([dest_id])
    src = BFS(src_id)
    dest = BFS(dest_id)

    while src.queue and dest.queue:
        src.curr = src.queue.pop()
        dest.curr = dest.queue.pop()
        if src.curr in dest.visited or dest.curr in src.visited:
            meeting_point = src.curr if src.curr in dest.visited else dest.curr
            src_path = list(reversed(trace_path(src.parents, src.id, meeting_point)))
            dest_path = trace_path(dest.parents, dest.id, dest.parents[meeting_point])
            return src_path + dest_path
        src.visit_neighbors()
        dest.visit_neighbors()
    return []

for artist in get_path(sys.argv[1], sys.argv[2]):
    print(artist)