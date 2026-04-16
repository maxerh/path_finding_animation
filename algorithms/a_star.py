import math
import heapq
from helpers import haversine

def algo_astar(G, source, target):
    dist = {source: 0}
    prev = {source: None}
    visited = []
    pq = [(haversine(G, source, target), 0, source)]
    in_pq = {source}
    while pq:
        f, d, u = heapq.heappop(pq)
        if u in [v for v, _ in visited]:
            continue
        visited.append((u, d))
        in_pq.discard(u)
        if u == target:
            break
        for _, v, data in G.edges(u, data=True):
            w = data.get("length", 1)
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd + haversine(G, v, target), nd, v))
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    if path[0] != source:
        return visited, []
    return visited, path
