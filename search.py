from typing import List, Dict, Set
import db
import collections
import sys

class BFS:
    def __init__(self, node_id: str):
        self.id = node_id
        self.queue = collections.deque([node_id])
        self.curr: str = ''
        self.parents: Dict[str, str] = {}
        self.visited: Set[str] = set()

    def visit_neighbors(self) -> None:
        for neighbor in db.get_related_artists(self.curr):
            if neighbor in self.visited:
                continue
            self.queue.appendleft(neighbor)
            self.parents[neighbor] = self.curr
            self.visited.add(neighbor)

def trace_path(parents: Dict[str, str], src: str, dest: str) -> List[str]:
    path = [dest]
    while path[-1] != src:
        path.append(parents[path[-1]])
    ids = [db.get_name(artist_id) for artist_id in path]
    return list(filter(None, ids))

def get_path(src_name: str, dest_name: str) -> List[str]:
    src_id = db.get_id(src_name)
    dest_id = db.get_id(dest_name)
    if not src_id or not dest_id:
        return []

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

if __name__ == '__main__':
    for artist in get_path(sys.argv[1], sys.argv[2]):
        print(artist)
