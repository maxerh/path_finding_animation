from collections import deque
from helpers import reconstruct


def algo_bfs(G, source, target, weight='length'):
    visited = []
    prev = {source: None}
    queue = deque([source])
    seen = {source}
    while queue:
        u = queue.popleft()
        visited.append((u, len(visited)))
        if u == target:
            break
        for _, v in G.edges(u):
            if v not in seen:
                seen.add(v)
                prev[v] = u
                queue.append(v)
    return visited, reconstruct(prev, source, target)