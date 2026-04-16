import math
from helpers import reconstruct


def algo_bellman_ford(G, source, target, weight='length'):
    dist = {n: math.inf for n in G.nodes}
    dist[source] = 0
    prev: dict = {source: None}
    visited = []
    edges = [(u, v, d.get(weight, 1)) for u, v, d in G.edges(data=True)]
    n = min(len(G.nodes), 600)
    for _ in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] < math.inf and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                visited.append((v, dist[v]))
                updated = True
        if not updated:
            break
    return visited, reconstruct(prev, source, target)