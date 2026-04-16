import math
import heapq
from helpers import reconstruct


def algo_dijkstra(G, source, target, weight='length'):
    dist = {source: 0}
    prev = {source: None}
    visited = []
    seen = set()
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
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
                heapq.heappush(pq, (nd, v))
    return visited, reconstruct(prev, source, target)
