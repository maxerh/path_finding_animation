import math
import heapq


def algo_dijkstra(G, source, target):
    dist = {source: 0}
    prev = {source: None}
    visited = []
    pq = [(0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if u in [v for v, _ in visited]:
            continue
        visited.append((u, d))
        if u == target:
            break
        for _, v, data in G.edges(u, data=True):
            w = data.get("length", 1)
            nd = d + w
            if nd < dist.get(v, math.inf):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    # Reconstruct path
    path = []
    cur = target
    while cur is not None:
        path.append(cur)
        cur = prev.get(cur)
    path.reverse()
    if path[0] != source:
        return visited, []
    return visited, path

