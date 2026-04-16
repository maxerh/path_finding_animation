import math
import heapq
from helpers import haversine, reconstruct

def algo_astar(G, source, target, weight='length'):
    dist = {source: 0}
    prev = {source: None}
    visited = []
    seen = set()
    pq = [(haversine(G, source, target), 0, source)]
    while pq:
        f, d, u = heapq.heappop(pq)
        if u in seen:
            continue
        seen.add(u)
        visited.append((u, d))
        if u == target:
            break
        for _, v, data in G.edges(u, data=True):
            w = data.get(weight, 1)
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd + haversine(G, v, target), nd, v))
    return visited, reconstruct(prev, source, target)